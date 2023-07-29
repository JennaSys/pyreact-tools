#!/usr/bin/env python3
import sys

import lxml.html
import argparse
import pyperclip


"""
Converts a JSX fragment to a Python function equivalent

Example:

<div id="root"><Button radius="md" size="lg" compact uppercase>Settings</Button></div>

Div({'id': 'root'},
    Button({'radius': 'md', 'size': 'lg', 'compact': True, 'uppercase': True}, "Settings")
)
"""


# Not all attribute values need to be strings...
def to_num(str_val):
    try:
        if str_val.lower() in ['true', 'false']:
            return str_val.lower() == 'true'
        elif '.' in str_val:
            return float(str_val)
        else:
            return int(str_val)

    except ValueError:
        return str_val


# Fixes escaped attribute values and attribute singletons,
def clean_vals(jsx):
    jsx_parts = [f'{child}'.strip() for child in jsx.split('>')][:-1]
    new_jsx = []
    for part in jsx_parts:
        if part[0] == '<':
            attribs = part.split()
            new_attribs = []
            in_quote = False
            end_tag = False
            for attrib in attribs:
                if attrib[0] == '<':  # Skip tag
                    new_attribs.append(attrib)
                    continue

                end_quote = attrib.strip()[-1] in ["'", '"']
                in_quote = any([in_quote, "'" in attrib, '"' in attrib]) and not end_quote
                if in_quote or end_quote:  # Skip quoted strings
                    new_attribs.append(attrib)
                    continue

                if not end_tag and '=' not in attrib and attrib[-1:] != '/':  # Handle boolean attributes with no value
                    attrib = f'{attrib}=true'

                end_tag = not end_tag and attrib.strip()[-1] == '>'

                new_attribs.append(attrib.replace('{', '').replace('}', ''))  # Remove any {} from values
            new_jsx.append(f"{' '.join(new_attribs)}>")
        else:
            new_jsx.append(f"{part}>")

    # Put it all back together...
    return ''.join(new_jsx)


# Recursively turns JSX string into string of functions
def jsxtopy(jsx, level=1):
    INDENT = 4

    jsx_ = clean_vals(jsx)
    fragments = lxml.html.fragments_fromstring(jsx_)

    py_root = []
    child_str_lst = []
    tmp_jsx = jsx_

    for element in fragments:  # The jsx parameter could be a list of many elements, so loop through them all
        tag = tmp_jsx.strip().split('>')[0].split()[0][1:]  # lxml forces lower case so grab the tag name from the raw text, stripping off any attributes
        fmt_tag = tag.capitalize() if tag.islower() else tag  # Native HTML tags like 'div' need to get capitalized
        attribs = {k: to_num(v) for k, v in element.attrib.items()}  # Represent numeric values as numbers instead of strings

        # This sets things up for getting the proper tag next in the next pass through the loop
        tmp_str_lst = [f'<{child}'.strip() for child in tmp_jsx.split('<')][2:]
        if f'</{tag}>' in tmp_str_lst:
            idx = [tmp for tmp in tmp_str_lst].index(f'</{tag}>')
            if idx == 0:
                tmp_str_lst = tmp_str_lst[1:]
            elif idx > 0:
                child_str_lst = tmp_str_lst[:idx]  # If there are child elements between the opening and closing tage, save these fragments for later
                tmp_str_lst = tmp_str_lst[idx+1:]

        tmp_jsx = ''.join(tmp_str_lst)  # Put it all back together
        # print("tmp_jsx:", tmp_jsx)

        attrib_str = str(attribs) if len(element.attrib) > 0 else None  # Convert the whole attrib dict to a single string for later
        if len(element) > 0:  # There are child elements that need to be processed
            child_jsx = ''.join(child_str_lst)
            # print("child_jsx:", child_jsx)
            children = jsxtopy(child_jsx, level + 1)  # Do the child conversions first
            py_root.append(f'{fmt_tag}({attrib_str},\n{" " * INDENT * level}{children}\n{" " * INDENT * (level - 1)})')
        else:  # InnerHTML is just text here
            text_child = '' if element.text is None else f', "{element.text.strip()}"'
            py_root.append(f'{fmt_tag}({attrib_str}{text_child})')

    return f',\n{" "*INDENT*(level-1)}'.join(py_root)


def run(jsx):
    print(f"\njsx:\n{jsx}\n")
    pyified = jsxtopy(jsx)
    print(f"pyified:\n{pyified}\n")
    return pyified


def test():
    test_jsx = [
        '<div id="root">Loading...</div>',
        """<div id="root"><Button radius="md" size="lg" compact uppercase>Settings</Button></div>""",
        """<SimpleGrid cols={3}>
      <Text variant="outline">1</Text>
      <Text>2</Text><Text>3</Text>
      <Text>4</Text>
      <Text>5</Text>
    </SimpleGrid>""",
        """<Group>
              <Button variant="outline">1</Button>
              <Button variant="outline">2</Button>
              <Button p={3} radius="sm md" size="lg" compact uppercase>
  Settings
</Button>
              <Switch
      labelPosition="left"
      label="I agree to sell my privacy"
      size="md"
      radius="lg"
      color="red"
      disabled
    />
            </Group>""",
        """<Group>
              <Button variant="outline">1</Button>
              <Button variant="outline">2</Button>
              <Button p={5.2} radius="sm md" size="lg" compact uppercase>
  Settings
</Button>
              <Switch
      labelPosition="left"
      label="I agree to sell my privacy"
      size="md"
      radius="lg"
      color="red"
      disabled
    />
    <SimpleGrid cols={3}>
      <div>1</div>
      <div mx=7 my=2>2</div>
      <div>3</div>
      <div>4</div>
      <div>5</div>
    </SimpleGrid>
    <MultiSelect
      data={data}
      label="Your favorite frameworks/libraries"
      placeholder="Pick all that you like"
    />
            </Group>"""
    ]

    for jsx in test_jsx:
        print(f"jsx:\n{jsx}\n")
        pyified = jsxtopy(jsx)
        print(f"pyified:\n{pyified}\n")
        print()


def main():
    parser = argparse.ArgumentParser(prog='jsxtopy.py', description='Converts a JSX fragment to a Python function equivalent')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("'jsx'", help="JSX string to convert (If not supplied, will try to use what is in clipboard)", nargs='?', const='JSX copied from clipboard')
    group.add_argument("--test", help="Run test JSX", action="store_true")
    args = parser.parse_args()

    if args.test:
        print("--- TESTING ---\n")
        test()
    else:
        if len(sys.argv) > 1:
            jsx_text = sys.argv[1]
            run(jsx_text)
            # print("sys.argv:", sys.argv)
        else:
            jsx_text = pyperclip.paste()
            if jsx_text and jsx_text.strip()[0] == '<' and jsx_text.strip()[-1] == '>':
                result = run(jsx_text)
                pyperclip.copy(result)
            else:
                print("ERROR: Invalid JSX in clipboard!")


if __name__ == '__main__':
    main()
