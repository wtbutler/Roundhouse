import re, os, json
import pkg_resources as thisdir

json_folder = 'guild-json/'

async def add_macro(ctx, pattern, target, test):
    if not ctx.guild:
        return False, "Must be in a server to store macros"
    try:
        a = re.compile(pattern)
        match = a.match(test)
        b = match.expand(target)
    except Exception as e:
        print(e)
        return False, f"Regex not valid"
    json_file = json_folder + str(ctx.guild.id) + ".json"
    json_file = thisdir.resource_filename(__name__, json_file)
    if os.path_exists(json_file):
        with open(json_file) as infile:
            json_data = json.load(infile)
    else:
        json_data = {'macros':[]}
    macro_patterns = [macro['pattern'] for macro in json_data['macros']]
    if pattern in macro_patterns:
        return False, "Pattern already has a target"
    if len(json_data['macros']) >= 50:
        return False, f"Too many regexes saved, can't add any more"
    json_data['macros'] += [{'pattern': pattern, 'target': target}]
    with open(json_file, 'w+') as outfile:
        json.dump(json_data, outfile, indent=4, sort_keys=True)
    return True, f"{b}"

async def remove_macro(ctx, macro):
    if not ctx.guild:
        return "Must be in a server to store macros"
    json_file = json_folder + str(ctx.guild.id) + ".json"
    json_file = thisdir.resource_filename(__name__, json_file)
    if os.path.exists(json_file):
        with open(json_file) as infile:
            json_data = json.load(infile)
    else:
        return "No macros on this server"
    if len(json_data['macros']) == 0:
        return "No macros on this server"
    if len(json_data['macros']) >= macro:
        a = json_data['macros'].pop(macro-1)
        with open(json_file, 'w+') as outfile:
            json.dump(json_data, outfile, indent=4, sort_keys=True)
        return f"macro `<Pattern: {a['pattern']}, Target: {a['target']}>` deleted"
    else:
        return "Not a valid macro to delete"

async def expand_macro(ctx, request):
    if not ctx.guild:
        return None
    json_file = json_folder + str(ctx.guild.id) + ".json"
    json_file = thisdir.resource_filename(__name__, json_file)
    if os.path.exists(json_file):
        with open(json_file) as infile:
            json_data = json.load(infile)
    else:
        return None
    if len(json_data['macros']) == 0:
        return None
    for macro in json_data['macros']:
        p = re.compile(macro['pattern'])
        match = p.match(request)
        if match:
            return match.expand(macro['target'])
    return None

async def list_macros(ctx):
    if not ctx.guild:
        return "Must be in a server to store macros"
    json_file = json_folder + str(ctx.guild.id) + ".json"
    json_file = thisdir.resource_filename(__name__, json_file)
    if os.path.exists(json_file):
        with open(json_file) as infile:
            json_data = json.load(infile)
    else:
        return "No macros on this server"
    items = []
    if len(json_data['macros']) == 0:
        return "No macros on this server"
    for i, macro in enumerate(json_data['macros']):
        items += [f"id: {i+1}  Pattern: {macro['pattern']}   Target: {macro['target']}"]
    string = '\n'.join(items)
    return f"```{string}```"
