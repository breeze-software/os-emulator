import json
from copy import deepcopy

import utils


def add_file(out, content, tags, _from):
    h = utils.calc_hash(content)
    out["files"][h] = {
        "data": content,
        # "tags": tags,
        # "when_modified": [utils.get_time()],
        # "when_accessed": [],
        "from": _from,
    }
    return out


def build_file(content, tags, _from):
    h = utils.calc_hash(content)
    return (
        h,
        {
            "data": content,
            # "tags": tags,
            # "when_modified": [utils.get_time()],
            # "when_accessed": [],
            "from": _from,
        },
    )


def build_source(sources, s):
    return build_file(content=sources[s]["data"], tags=[], _from={})


def build_function(functions, binaries, sources, f, p):
    return build_file(
        content=functions[f]["data"],
        tags=[],
        _from={binaries[p]["hash"]: [sources[f]["hash"]]},
    )


def build_binary(binaries, programs, compiler, s):
    return build_file(
        content=binaries[s]["data"],
        tags=[],
        _from={binaries[compiler]["hash"]: [programs[s]["hash"]]},
    )


def add_system_function(out, name):
    s = f"[BINARY CONTENT ({name})]"
    h = utils.calc_hash(s)
    out["system_functions"][h] = s
    out["programs"][name] = h
    return out


def add_function(out, f):
    h = utils.calc_hash(f)
    out["files"][h] = {"data": f}
    return out


def add_program(out, name, spec):
    p = ["spec", {"entry": spec}]
    h = utils.calc_hash(p)
    out["programs"][name] = h
    out["permissions"][h] = {
        "file (read)": True,
        "file (write)": False,
        "network (incoming)": False,
        "network (outgoing)": False,
    }
    out = add_file(out, content=p, tags=[])
    return out


def permissions():
    return {
        "file (read)": True,
        "file (write)": False,
        "network (incoming)": False,
        "network (outgoing)": False,
    }


def get_sources():
    sources = {
        "parser-a": {
            "data": "this is fake source code that is parsed via 'parser-a' into a Language A parser"
        },
        "parser-b": {
            "data": "this is fake source code that is parsed via 'parser-a' into a Language B parser"
        },
        "parser-spec": {
            "data": "this is fake source code that is parsed via 'parser-a' into a Language Spec parser"
        },
        "compile-default": {
            "data": "this is fake source code that is parsed via 'parser-a' into a compiler"
        },
        "foo": {"data": "fake source code: [foo]"},
        "baz": {"data": "fake source code: [baz]"},
        "bar-foo": {"data": "fake source code: [bar [foo]]"},
        "bar-foo-baz": {"data": "fake source code: [[bar [foo]] baz]"},
        "aaa": {"data": "fake source code: [aaa]"},
        "bbb": {"data": "fake source code: [bbb]"},
        "ooo": {"data": "fake source code: [ooo]"},
    }
    for k in sources.keys():
        sources[k]["hash"] = utils.calc_hash(sources[k]["data"])
    return sources


def get_parsers():
    parsers = {
        "parser-a": {"data": ["parse", ["text", "Language A"]]},
        "parser-b": {"data": ["parse", ["text", "Language B"]]},
        "parser-spec": {"data": ["parse", ["text", "Language Spec"]]},
    }
    for k in parsers.keys():
        parsers[k]["hash"] = utils.calc_hash(parsers[k]["data"])
    return parsers


def get_functions():
    f = lambda data: {"data": data, "hash": utils.calc_hash(data)}
    functions = {
        "aaa": f(["aaa"]),
        "bbb": f(["bbb"]),
        "ooo": f(["ooo"]),
        "foo": f(["foo"]),
        "baz": f(["baz"]),
        "bar-foo": f(["bar", utils.calc_hash(["foo"])]),
        "bar-foo-baz": f([utils.calc_hash(["bar", utils.calc_hash(["foo"])]), "baz"]),
    }
    return functions


def get_programs(functions):
    programs = {
        "apple": {"data": [{"entry": functions["aaa"]["hash"]}]},
        "orange": {"data": [{"entry": functions["ooo"]["hash"]}]},
        "banana": {"data": [{"entry": functions["bbb"]["hash"]}]},
        "parser-a": {"data": [{"entry": functions["foo"]["hash"]}]},
        "parser-b": {"data": [{"entry": functions["baz"]["hash"]}]},
        "parser-spec": {"data": [{"entry": functions["bar-foo"]["hash"]}]},
        "compile-default": {"data": [{"entry": functions["bar-foo-baz"]["hash"]}]},
    }
    for k in programs.keys():
        programs[k]["hash"] = utils.calc_hash(programs[k]["data"])
    return programs


def get_binaries():
    binaries = {}
    for s in [
        "compile-default",
        "parser-a",
        "parser-b",
        "parser-spec",
        "list",
        "print",
        "apple",
        "orange",
        "banana",
    ]:
        binaries[s] = {"data": f"[BINARY CONTENT ({s})]"}
    for k in binaries.keys():
        binaries[k]["hash"] = utils.calc_hash(binaries[k]["data"])
    return binaries


def parse():
    sources = get_sources()
    parsers = get_parsers()
    functions = get_functions()
    programs = get_programs(functions)
    binaries = get_binaries()

    out = {"files": {}, "programs": {}, "permissions": {}, "system_functions": {}}

    for s in sources.keys():
        h, func = build_source(sources, s)
        out["files"][h] = func

    for f in functions.keys():
        h, func = build_function(functions, binaries, sources, f, "parser-a")
        out["files"][h] = func

    for k in programs.keys():
        out = add_file(out, content=programs[k]["data"], tags=[], _from={})

    for s in binaries.keys():
        if s in ["print", "list"]:
            out["system_functions"][s] = binaries[s]["hash"]
        else:
            h, b = build_binary(binaries, programs, "compile-default", s)
            out["files"][h] = b
            out["programs"][s] = h
            out["permissions"][h] = permissions()

    """

    out = add_file(
        out,
        content="this is just a text note",
        tags=["stuff", "other", "text"],
        _from={},
    )
    out = add_file(out, content="another text note", tags=["text"], _from={})
    for s in ["parser-a", "parser-b", "parser-spec", "compile-default"]:
        h, data = build_source(sources, s)
        out["files"][h] = data

    out = add_file(
        out,
        content=parsers["parser-a"]["data"],
        tags=[],
        _from={parsers["parser-a"]["hash"]: [sources["parser-a"]["hash"]]},
    )
    out = add_file(
        out,
        content=parsers["parser-b"]["data"],
        tags=[],
        _from={parsers["parser-a"]["hash"]: [sources["parser-b"]["hash"]]},
    )


    out = add_file(out, content=programs["apple"]["data"], tags=[], _from={})


    for s in ["foo", "baz", "bar-foo"]:
        out = add_file(out, content=functions[s]["data"], tags=[], _from={})
    """

    return out


def temp___():
    out = add_file(
        out,
        content="this is fake source code that is parsed via 'parser-a' into a Language B parser",
        tags=[],
    )

    out = add_function(out, ["foo"])
    out = add_function(out, ["bar", "hash:" + utils.calc_hash(["foo"])])
    out = add_function(out, ["baz"])

    out = add_function(out, ["parse", "Language A"])
    out = add_function(out, ["parse", "Language B"])

    out = add_function(out, ["compile", "default"])

    out = add_program(out, name="apple", spec=utils.calc_hash(["foo"]))
    out = add_program(
        out,
        name="orange",
        spec=utils.calc_hash([["bar", "hash:" + utils.calc_hash(["foo"])]]),
    )
    out = add_program(out, name="banana", spec=utils.calc_hash(["baz"]))

    out = add_program(
        out, name="parse-a", spec=utils.calc_hash(["parse", "Language A"])
    )
    out = add_program(
        out, name="parse-b", spec=utils.calc_hash(["parse", "Language B"])
    )

    out = add_program(
        out, name="compile-default", spec=utils.calc_hash(["compile", "default"])
    )

    for h in [
        "16d120da...",
        "3b3ec66a...",
        "46068258...",
        "4ff2a550...",
        "d173c165...",
    ]:
        out["files"][h]["parser"] = out["programs"]["parse-a"]
        out["files"][h]["compiler"] = out["programs"]["compile-default"]

    out["files"]["a660f78a..."]["parser"] = out["programs"]["parse-b"]
    out["files"]["a660f78a..."]["compiler"] = out["programs"]["compile-default"]

    return out
