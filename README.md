# PyReact Tools

## [jsxtopy](https://github.com/JennaSys/pyreact-tools/blob/main/jsxtopy.py)
### Converts a JSX fragment to a Python function equivalent
I got tired of having to manually convert JSX code to Python functions with dictionary attributes and having to manually quote everything when copying JSX example code from somewhere to use in my React Python projects, so I created this function that will (mostly) do it for me.

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

## Resources
- https://pyreact.com
- https://www.transcrypt.org