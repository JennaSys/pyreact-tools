# PyReact Tools

## [jsxtopy](https://github.com/JennaSys/pyreact-tools/blob/main/jsxtopy.py)
### Converts a JSX fragment to a Python function equivalent
When copying JSX example code from somewhere to use in my React Python projects, I got tired of having to manually convert JSX code to Python functions with dictionary attributes and having to manually quote everything. So I created this function that will (mostly) do it for me.

For example, this JSX code:
```jsx
<div id="root"><Button radius="md" size="lg" compact uppercase>Settings</Button></div>
```
will get converted to this Python code:
```python
Div({'id': 'root'},
    Button({'radius': 'md', 'size': 'lg', 'compact': True, 'uppercase': True}, "Settings")
)
```

## Usage:
```text
usage: jsxtopy.py [-h] [--test] ['jsx']

Converts a JSX fragment to a Python function equivalent

positional arguments:
  'jsx'       JSX string to convert (If not supplied, will try to use what is in clipboard)

optional arguments:
  -h, --help  show this help message and exit
  --test      Run test JSX
```

## Resources
- https://pyreact.com
- https://www.transcrypt.org