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


# Not all attribute values need to be strings...
def to_num(str_val):
    if str_val:
        try:
            if str_val.lower() in ['true', 'false']:
                return str_val.lower() == 'true'
            elif '.' in str_val:
                return float(str_val)
            elif str_val[0] == '[' and str_val[-1] == ']':
                return ast.literal_eval(str_val)
            else:
                return int(str_val)

        except ValueError:
            return str_val
    else:
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
            in_array = False
            end_tag = False
            for attrib in attribs:
                if attrib[0] == '<':  # Skip tag But fix fragment
                    if attrib.strip() == '<' or attrib.strip() == '</':  # Fragment
                        attrib = f'{attrib.strip()}Fragment'
                    new_attribs.append(attrib)
                    continue

                # Handle array as value
                if not in_array:
                    if "[" in attrib:
                        in_array = True
                        attrib = attrib.replace('{[', '"[').replace('{ [', '"[')
                else:
                    if "]" in attrib:
                        in_array = False
                        attrib = attrib.replace(']}', ']"').replace('] }', ']"')

                end_quote = attrib.strip()[-1] in ["'", '"']
                in_quote = any([in_quote, "'" in attrib, '"' in attrib]) and not (end_quote or in_array)
                if in_quote or end_quote or in_array:  # Skip quoted strings
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


# Recursively turns JSX string into string of function calls
def jsxtopy(jsx, use_dict, level=1):
    INDENT = 4

    jsx_ = clean_vals(jsx)
    fragments = lxml.html.fragments_fromstring(jsx_)

    py_root = []
    child_str_lst = []
    tmp_jsx = jsx_

    for element in fragments:  # The jsx parameter could be a list of many elements, so loop through them all
        tag = tmp_jsx.strip().split('>')[0].split()[0][1:] if tmp_jsx.strip() else '' # lxml forces lower case so grab the tag name from the raw text, stripping off any attributes
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

        # Convert the whole attrib dict to a single string for later
        if len(element.attrib) > 0:
            if use_dict:
                attrib_str = ''.join(['dict(', ', '.join([f"{k}={repr(v)}" for k, v in attribs.items()]), ')'])
            else:
                attrib_str = str(attribs)
        else:
            attrib_str = None

        if len(element) > 0:  # There are child elements that need to be processed
            child_jsx = ''.join(child_str_lst)
            # print("child_jsx:", child_jsx)
            children = jsxtopy(child_jsx, use_dict, level + 1)  # Do the child conversions first
            py_root.append(f'{fmt_tag}({attrib_str},\n{" " * INDENT * level}{children}\n{" " * INDENT * (level - 1)})')
        else:  # Child is likely just text here
            text_child = '' if element.text is None else f', "{element.text.strip()}"'
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
    test_jsx = ["""<Select
      maw={320}
      mx="auto"
      label="Your favorite framework/library"
      placeholder="Pick one"
      data={['React', 'Angular', 'Svelte', 'Vue']}
      transitionProps={{ transition: 'pop-top-left', duration: 80, timingFunction: 'ease' }}
      withinPortal
    />"""]

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
    # TODO: Handle object as attribute value {{ }}  ->  { }
    # TODO: Handle JSX as attribute value
    # TODO: Handle function as attribute value

    main()
