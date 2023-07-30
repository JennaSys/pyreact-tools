import jsxtopy


def test_empty_native_element():
    jsx = """<div></div>"""

    result = jsxtopy.run(jsx)
    assert result == """Div(None)"""


def test_native_element_with_text():
    jsx = """<div>This is text</div>"""

    result = jsxtopy.run(jsx)
    assert result == """Div(None, "This is text")"""


def test_fragment_with_children_attribs_text():
    jsx = """<>
        <div>1</div>
      <div mx=5 my="lg">2</div>
      <div>3</div>
      </>
        """

    result = jsxtopy.run(jsx)
    assert result == """Fragment(None,
    Div(None, "1"),
    Div({'mx': 5, 'my': 'lg'}, "2"),
    Div(None, "3")
)"""


def test_element_with_attrib_and_text():
    jsx = """<div id="root">This is text with attrib</div>"""

    result = jsxtopy.run(jsx)
    assert result == """Div({'id': 'root'}, "This is text with attrib")"""


def test_element_with_attrib_and_child_and_text():
    jsx = """<div id="root"><Button radius="md" size="lg" compact uppercase>Settings</Button></div>"""

    result = jsxtopy.run(jsx)
    assert result == """Div({'id': 'root'},
    Button({'radius': 'md', 'size': 'lg', 'compact': True, 'uppercase': True}, "Settings")
)"""


def test_selfclosed_component_with_attrib_having_array_value():
    jsx = """<NativeSelect
              data={['React', 'Vue', 'Angular', 'Svelte']}
              label="Select your favorite framework/library"
              description="This is anonymous"
              withAsterisk
            />"""

    result = jsxtopy.run(jsx)
    assert result == """NativeSelect({'data': ['React', 'Vue', 'Angular', 'Svelte'], 'label': 'Select your favorite framework/library', 'description': 'This is anonymous', 'withasterisk': True})"""


def test_selfclosed_component_with_attrib_having_array_value_usedict():
    jsx = """<NativeSelect
              data={['React', 'Vue', 'Angular', 'Svelte']}
              label="Select your favorite framework/library"
              description="This is anonymous"
              withAsterisk
            />"""

    result = jsxtopy.run(jsx, use_dict=True)
    assert result == """NativeSelect(dict(data=['React', 'Vue', 'Angular', 'Svelte'], label='Select your favorite framework/library', description='This is anonymous', withasterisk=True))"""


def test_component_withandwithout_attrib_and_children_and_numvals_and_text():
    jsx = """<SimpleGrid cols={3}>
      <Text variant="outline">1</Text>
      <Text>2</Text><Text>3</Text>
      <Text>4</Text>
      <Text>5</Text>
    </SimpleGrid>"""

    result = jsxtopy.run(jsx)
    assert result == """SimpleGrid({'cols': 3},
    Text({'variant': 'outline'}, "1"),
    Text(None, "2"),
    Text(None, "3"),
    Text(None, "4"),
    Text(None, "5")
)"""


def test_nested_component_group_withandwithout_attrib_and_children_and_numvals_and_text():
    jsx = """<Group>
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
            </Group>"""

    result = jsxtopy.run(jsx)
    assert result == """Group(None,
    Button({'variant': 'outline'}, "1"),
    Button({'variant': 'outline'}, "2"),
    Button({'p': 3, 'radius': 'sm md', 'size': 'lg', 'compact': True, 'uppercase': True}, "Settings"),
    Switch({'labelposition': 'left', 'label': 'I agree to sell my privacy', 'size': 'md', 'radius': 'lg', 'color': 'red', 'disabled': True})
)"""


def test_nested_component_with_everything():
    jsx = """<Group>
              <Button variant="outline">1</Button>
              <Button variant="outline">2</Button>
              <NativeSelect
              data={['React', 'Vue', 'Angular', 'Svelte']}
              label="Select your favorite framework/library"
              description="This is anonymous"
              withAsterisk
            />
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

    result = jsxtopy.run(jsx)
    assert result == """Group(None,
    Button({'variant': 'outline'}, "1"),
    Button({'variant': 'outline'}, "2"),
    NativeSelect({'data': ['React', 'Vue', 'Angular', 'Svelte'], 'label': 'Select your favorite framework/library', 'description': 'This is anonymous', 'withasterisk': True}),
    Button({'p': 5.2, 'radius': 'sm md', 'size': 'lg', 'compact': True, 'uppercase': True}, "Settings"),
    Switch({'labelposition': 'left', 'label': 'I agree to sell my privacy', 'size': 'md', 'radius': 'lg', 'color': 'red', 'disabled': True}),
    SimpleGrid({'cols': 3},
        Div(None, "1"),
        Div({'mx': 7, 'my': 2}, "2"),
        Div(None, "3"),
        Div(None, "4"),
        Div(None, "5")
    ),
    MultiSelect({'data': 'data', 'label': 'Your favorite frameworks/libraries', 'placeholder': 'Pick all that you like'})
)"""


