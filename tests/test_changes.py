from tests.changes import diff


def tags(data):
    return [i["tag"] for i in data]


def some_system(cls, *instances):
    return {"system": cls.lower(), "class": cls, "instances": list(instances)}


def some_multi_system(name, *systems):
    ret = {"system": name, "class": {}}
    for system in systems:
        ret["class"][system["class"]] = {"instances": system["instances"]}
    return ret


def test_changed_instance():
    a = some_system("example", {"tag": "foo", "x": 1}, {"tag": "bar", "x": 2})
    b = some_system("example", {"tag": "foo", "x": 1}, {"tag": "bar", "x": 3})
    assert ["bar"] == tags(diff(a, b))


def test_removed_instance():
    a = some_system("example", {"tag": "foo", "x": 1})
    b = some_system("example", {"tag": "foo", "x": 1}, {"tag": "bar", "x": 3})
    assert not tags(diff(a, b))


def test_added_instance():
    a = some_system("example", {"tag": "foo", "x": 1})
    b = some_system("example", {"tag": "foo", "x": 1}, {"tag": "bar", "x": 3})
    assert ["bar"] == tags(diff(b, a))


def test_order_instance():
    a = some_system("example", {"tag": "foo", "x": 1}, {"tag": "bar", "x": 3})
    b = some_system("example", {"tag": "bar", "x": 3}, {"tag": "foo", "x": 1})
    assert not tags(diff(a, b))


def test_no_prev():
    a = some_system("example", {"tag": "foo", "x": 1}, {"tag": "bar", "x": 3})
    assert ["foo", "bar"] == tags(diff(a, {}))


def test_multi_changed():
    a = some_multi_system(
        "example",
        some_system("example_a", {"tag": "foo", "x": 1}, {"tag": "bar", "x": 42}),
        some_system("example_b", {"tag": "baz", "x": 42}, {"tag": "fuz", "x": 1}),
    )
    b = some_multi_system(
        "example",
        some_system("example_a", {"tag": "foo", "x": 1}, {"tag": "bar", "x": 1}),
        some_system("example_b", {"tag": "baz", "x": 1}, {"tag": "fuz", "x": 1}),
    )
    assert ["bar", "baz"] == tags(diff(a, b))
