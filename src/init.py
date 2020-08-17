import json
from copy import deepcopy

import utils


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
    h, out = build_file(content=sources[s]["data"], tags=[], _from={})
    out["type"] = "source"
    return h, out


def build_function(functions, binaries, sources, f, p):
    h, out = build_file(
        content=functions[f]["data"],
        tags=[],
        _from={binaries[p]["hash"]: [sources[f]["hash"]]},
    )
    out["type"] = "function"
    return h, out


def build_program(programs, p):
    h, out = build_file(content=programs[p]["data"], tags=[], _from={})
    out["type"] = "program spec"
    return h, out


def build_binary(binaries, programs, compiler, s):
    h, out = build_file(
        content=binaries[s]["data"],
        tags=[],
        _from={binaries[compiler]["hash"]: [programs[s]["hash"]]},
    )
    out["type"] = "binary"
    return h, out


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
        h, p = build_program(programs, k)
        out["files"][h] = p

    for s in binaries.keys():
        if s in ["print", "list"]:
            out["system_functions"][s] = binaries[s]["hash"]
        else:
            h, b = build_binary(binaries, programs, "compile-default", s)
            out["files"][h] = b
            out["programs"][s] = h
            out["permissions"][h] = permissions()

    return out
