#!/usr/bin/env python3

import ast
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


def quote_dict(str_dict):
    dict_items = [item.split(':') for item in str_dict.strip()[1:-1].split(',')]
    quoted_items = [f"""{k.strip() if k[0] in ['"', "'"] else f"'{k.strip()}'"}: {v}""" for k, v in dict_items]
    quoted_dict = f"{{{', '.join(quoted_items)}}}"
    return quoted_dict


# Not all attribute values need to be strings...
def fmt_val(str_val, use_dict):
    if str_val:
        try:
            if str_val[0] == '{' and str_val[-1] == '}':
                quoted_dict = quote_dict(str_val)  # Make sure keys are quoted
                return ast.literal_eval(quoted_dict)
            elif str_val.strip()[0] == '<' and str_val.strip()[-1] == '>':  # JSX as value
                return jsxtopy(str_val.strip(), use_dict)
            elif str_val.lower() in ['true', 'false']:
                return str_val.lower() == 'true'
            elif '.' in str_val:
                return float(str_val)
            elif str_val[0] == '[' and str_val[-1] == ']':
                if '{' in str_val and '}' in str_val:  #Assume list of dicts
                    new_list = []
                    for item in str_val.strip()[1:-1].split('}'):
                        item = item.strip().strip(',').strip()  # Remove any leading or trailing commas
                        if not item:
                            continue

                        if item[0] == '{':  # Make sure this is a dict
                            new_list.append(ast.literal_eval(quote_dict(f"{item}}}")))
                        else:
                            new_list.append(item)
                    return new_list
                else:
                    return ast.literal_eval(str_val)
            else:
                return int(str_val)

        except ValueError:
            return str_val
    else:
        return str_val


# Fixes escaped attribute values and attribute singletons,
def clean_vals(jsx):
    jsx_parts = [f'{child}'.strip() for child in jsx.split('>')]
    new_jsx = []
    in_jsx_value = False
    for part in jsx_parts:
        if not part:
            continue

        if part[0] == '<' or in_jsx_value:
            attribs = part.split()
            new_attribs = []
            in_quote = False
            in_array = False
            in_dict = False
            end_tag = False
            for attrib in attribs:
                if attrib[0] == '<':  # Skip tag But fix fragment
                    if attrib.strip() == '<' or attrib.strip() == '</':  # Fragment
                        attrib = f'{attrib.strip()}Fragment'
                    new_attribs.append(attrib)
                    continue

                # Handle array as value by quoting it for now
                if not in_array:
                    if "[" in attrib:
                        in_array = True
                        attrib = attrib.replace('{[', '"[').replace('{ [', '"[')
                else:
                    if "]" in attrib:
                        in_array = False
                        attrib = attrib.replace(']}', ']"').replace('] }', ']"')

                # Handle dict as value by quoting it for now
                if not in_dict:
                    if "{{" in attrib:
                        in_dict = True
                        attrib = attrib.replace('{{', '"{').replace('{ {', '"{')
                else:
                    if "}}" in attrib:
                        in_dict = False
                        attrib = attrib.replace('}}', '}"').replace('} }', '}"')

               # Handle JSX as value by quoting it for now
                if not in_jsx_value:
                    if "{<" in attrib or "{ <" in attrib:
                        in_jsx_value = True
                        attrib = attrib.replace("{<", "'<").replace("{ <", "'<")
                else:
                    if attrib.strip()[0] == "}":
                        in_jsx_value = False
                        attrib = attrib.replace('}', "'")

                end_quote = attrib.strip()[-1] in ["'", '"']
                in_quote = any([in_quote, "'" in attrib, '"' in attrib]) and not any([end_quote, in_array, in_dict, in_jsx_value])
                if any([in_quote, end_quote, in_array, in_dict, in_jsx_value]):  # Skip quoted strings
                    new_attribs.append(attrib)
                    continue

                if not end_tag and '=' not in attrib and attrib[-1:] != '/':  # Handle boolean attributes with no value
                    attrib = f'{attrib}=true'

                end_tag = not end_tag and attrib.strip()[-1] == '>'

                new_attribs.append(attrib.replace('{', '').replace('}', ''))  # Remove any {} from values

            new_attribs_str = f"{' '.join(new_attribs)}>"
            new_jsx.append(new_attribs_str)  # JSX as attrib value might have uneccessary closing bracket
        else:
            new_jsx.append(f"{part}>")

    # Put it all back together...
    return ''.join(new_jsx)


# Recursively turns JSX string into string of function calls
def jsxtopy(jsx, use_dict, level=1):
    INDENT = 4

    jsx_ = clean_vals(jsx)
    fragments = lxml.html.fragments_fromstring(jsx_)

    py_root = []
    child_str_lst = []
    tmp_jsx = jsx_

    for element in fragments:  # The jsx parameter could be a list of many elements, so loop through them all
        if len(tmp_jsx) == 0:
            continue
        tag = tmp_jsx.strip().split('>')[0].split()[0][1:] if tmp_jsx.strip() else '' # lxml forces lower case so grab the tag name from the raw text, stripping off any attributes
        fmt_tag = tag.capitalize() if tag.islower() else tag  # Native HTML tags like 'div' need to get capitalized
        attribs = {k: fmt_val(v, use_dict) for k, v in element.attrib.items()}  # Represent numeric values as numbers instead of strings

        # This sets things up for getting the proper tag next in the next pass through the loop
        tmp_str_lst = [f'<{child}'.strip() for child in tmp_jsx.split('<')]
        tmp_str_lst = tmp_str_lst[2:] if any(['>' in item for item in tmp_str_lst[:2]]) else tmp_str_lst[3:]  # Skip over any JSX in attrib values
        if f'</{tag}>' in tmp_str_lst:
            idx = [tmp for tmp in tmp_str_lst].index(f'</{tag}>')
            if idx == 0:
                tmp_str_lst = tmp_str_lst[1:]
            elif idx > 0:
                child_str_lst = tmp_str_lst[:idx]  # If there are child elements between the opening and closing tage, save these fragments for later
                tmp_str_lst = tmp_str_lst[idx+1:]

        tmp_jsx = ''.join(tmp_str_lst)  # Put it all back together
        # print("tmp_jsx:", tmp_jsx)

        # Convert the whole attrib dict to a single string for later
        if len(element.attrib) > 0:
            if use_dict:
                attrib_str = ''.join(['dict(', ', '.join([f"{k}={repr(v)}" for k, v in attribs.items()]), ')'])
            else:
                attrib_str = str(attribs)
        else:
            attrib_str = None

        if len(element) > 0 or len(child_str_lst) > 0:  # There are child elements that need to be processed
            child_jsx = ''.join(child_str_lst)
            # print("child_jsx:", child_jsx)
            children = jsxtopy(child_jsx, use_dict, level + 1)  # Do the child conversions first
            py_root.append(f'{fmt_tag}({attrib_str},\n{" " * INDENT * level}{children}\n{" " * INDENT * (level - 1)})')
            child_str_lst = ''
        else:  # Child is likely just text here
            if element.text is not None:
                text_child = f', "{element.text.strip()}"'
            elif element.tail is not None:
                text_child = f', "{element.tail.strip()}"'
            else:
                text_child = ''

            py_root.append(f'{fmt_tag}({attrib_str}{text_child})')

    return f',\n{" "*INDENT*(level-1)}'.join(py_root)


def run(jsx, use_dict=False, verbose=False):
    if verbose:
        print(f"\njsx:\n{jsx}\n")
    pyified = jsxtopy(jsx, use_dict)

    if verbose:
        print(f"pyified:")
    print(f"\n{pyified}\n")

    return pyified


def run_dev(use_dict):
    test_jsx = [
        """<MultiSelect
  valueComponent={({ value, label, image, name }) => /* Your custom value component with data properties */}
  itemComponent={({ value, label, image, name }) => /* Your custom item component with data properties */}
  data={[
    {
      value: 'bob@handsome.inc',
      label: 'bob@handsome.inc',
      image: 'image-link',
      name: 'Bob Handsome',
    },
    {
      value: 'bill@outlook.com',
      label: 'bill@outlook.com',
      image: 'image-link',
      name: 'Bill Rataconda',
    },
    {
      value: 'amy@wong.cn',
      label: 'amy@wong.cn',
      image: 'image-link',
      name: 'Amy Wong',
    },
  ]}
/>"""
        ]

    print("--- DEV TESTING ---\n")
    for jsx in test_jsx:
        print(f"jsx:\n{jsx}\n")
        pyified = jsxtopy(jsx, use_dict)
        print(f"pyified:\n{pyified}\n")
        print()


def main():
    parser = argparse.ArgumentParser(prog='jsxtopy', description='Converts a JSX fragment to a Python function equivalent')
    group = parser.add_mutually_exclusive_group()
    parser.add_argument("-v", "--verbose", help="Print original JSX and Python result to console", action="store_true")
    parser.add_argument("-d", "--dict", help="Create props as dict function instead of dict literal", action="store_true")
    group.add_argument("jsx", help="JSX string to convert (If not supplied, will try to use what is in clipboard)", nargs='?', const='JSX copied from clipboard')
    group.add_argument("--test", help="Run JSX unit tests", action="store_true")
    group.add_argument("--dev", help="Run JSX development test", action="store_true")
    args = parser.parse_args()

    if args.test:
        import pytest
        import os

        module_dir = os.path.dirname(__file__)
        pytest.main(['-rA', os.path.join(module_dir, '../tests')])
    elif args.dev:
        run_dev(args.dict)
    else:
        if args.jsx:
            jsx_text = args.jsx
            run(jsx_text, use_dict=args.dict, verbose=args.verbose)
        else:
            if args.verbose:
                print("JSX not provided, using clipboard contents...")

            jsx_text = pyperclip.paste()
            if jsx_text and jsx_text.strip()[0] == '<' and jsx_text.strip()[-1] == '>':
                result = run(jsx_text, use_dict=args.dict, verbose=args.verbose)
                pyperclip.copy(result)
            else:
                print("ERROR: Invalid JSX in clipboard!")


if __name__ == '__main__':
    # TODO: Handle function as attribute value
    # TODO: Refactor to use re to try and clean up some of the hacky mess of code - ref gpt11 to get tags and gpt7 to lookup elements

    main()
