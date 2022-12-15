import random, re, numpy, operator
import macro_utils
from error_messages import error_messages

tokens = ["+", "-", "*", "/", "^", "(", ")"]
dice_cutoff_num = 1000

async def tokenize(request):
    tokenized = []
    temp_str = ""
    for char in request:
        if char == ' ':
            if temp_str:
                tokenized += [temp_str]
                temp_str = ""
        elif char not in tokens:
            temp_str += char
        else:
            if temp_str:
                tokenized += [temp_str]
                temp_str = ""
            tokenized += [char]
    if temp_str:
        tokenized += [temp_str]
        temp_str = ""
    return tokenized

async def error_message(error):
    return f"{random.choice(error_messages)}! ({error})"

async def handle_dice(ctx, message_in):
    repeat = [re.compile(r" *repeat *\( *(?P<command>.*) *, *(?P<count>[0-9]+) *\) *"),
        re.compile(r" *rp(?P<count>[0-9]+) +(?P<command>.*) *")]
    for target in repeat:
        match = target.match(message_in)
        if match:
            break
    if match:
        dic = match.groupdict()
        results = []
        for i in range(int(dic['count'])):
            results += [await handle_command(ctx, dic['command'])]
        if ',' in dic['command']:
            result = "\n\n".join(results)
        else:
            result = "\n".join(results)
        return result
    return await handle_command(ctx, message_in)

async def handle_command(ctx, message_in):
    roll_requests = [i.strip() for i in message_in.split(',')]
    roll_results = []
    for roll_request in roll_requests:
        roll_results += [await handle_request(ctx, roll_request)]
    return "\n".join(roll_results)

async def handle_request(ctx, roll_request):
    comment = re.compile(r"(?P<roll>.*?) *# *(?P<comment>.*)")
    match = comment.match(roll_request)
    comment = None
    if match:
        request = match.groupdict()['roll']
        comment = match.groupdict()['comment']
        print(comment)
    else:
        request = roll_request

    calculate = await tokenize(request)
    if ctx and ctx.guild:
        matched = False
        for i in range(len(calculate)):
            print(f"checking if {calculate[i]} is a macro")
            expanded = await macro_utils.expand_macro(ctx, calculate[i])
            if expanded:
                print("It is!")
                print(expanded)
                calculate[i] = f"({expanded})"
                print(calculate[i])
                matched = True
        if matched:
            print("We matched some stuff")
            request = ''.join(calculate)
            calculate = await tokenize(request)
    print(calculate)
    printable = calculate[:]
    request = ''.join(printable)

    for i in range(len(calculate)):
        if calculate[i] in tokens:
            continue
        for roll_func in options:
            rolls, result, error = await roll_func(calculate[i])
            if rolls or error:
                break
        if not rolls and not error:
            return await error_message(f"`{calculate[i]}` not recognized")
        elif error:
            return await error_message(error)
        else:
            calculate[i] = str(result)
            printable[i] = rolls
    for i in range(len(calculate)):
        if calculate[i] == '^':
            calculate[i] = '**'
    resulting_calc = ' '.join(calculate)
    print(resulting_calc)
    i_rolls = ''.join(printable)
    print(i_rolls)
    try:
        total = eval(resulting_calc)
    except SyntaxError as e:
        return await error_message(f"Invalid syntax")
    except ZeroDivisionError as e:
        return await error_message(f"Tried to divide by zero")
    if comment:
        return f"[{comment}] `{request}` = {i_rolls} = {total}"
    return f"`{request}` = {i_rolls} = {total}"

def get_operator(op_string):
    if op_string == "=":
        return operator.eq
    if op_string == "<":
        return operator.lt
    if op_string == ">":
        return operator.gt
    if op_string == "<=":
        return operator.le
    if op_string == ">=":
        return operator.ge
    return None

async def check_count_dice(message, roll_string):
    dice_roll = re.compile(rf"^{roll_string}{count_suffix}$")
    match = dice_roll.match(message)
    if match:
        print(f"Succeeds if die {match.groupdict()['operator']} {match.groupdict()['comp_num']}")
        if match.groupdict()['failure_vals']:
            print(f"Fails if die matches {match.groupdict()['failure_vals'].split('f')[1:]}")
        if match.groupdict()['failure_cond']:
            print(f"Fails if die {match.groupdict()['failure_cond']} {match.groupdict()['failure_cond_val']}")
        print("Matches count formula")
        return True, match
    return None, None

async def count_the_dice(message, roll_string, rolls):
    dice_roll = re.compile(rf"^{roll_string}{count_suffix}$")
    match = dice_roll.match(message)
    if match:
        print(f"Succeeds if die {match.groupdict()['operator']} {match.groupdict()['comp_num']}")
        info = match.groupdict()
        roll_strings = [str(i) for i in rolls]
        success_op = get_operator(info['operator'])
        s_cond_val = int(info['comp_num'])
        successes = 0
        if info['twice_vals']:
            t_vals = [int(i) for i in info['twice_vals'].split('t')[1:]]
            for i, die in enumerate(rolls):
                if success_op(die, s_cond_val):
                    successes += 1
                    if die in t_vals:
                        successes += 1
                    roll_strings[i] = f"**{roll_strings[i]}**"
        elif info['twice_cond']:
            twice_op = get_operator(info['twice_cond'])
            t_cond = int(info['twice_cond_val'])
            for i, die in enumerate(rolls):
                if success_op(die, s_cond_val):
                    successes += 1
                    if twice_op(die, t_cond):
                        successes += 1
                    roll_strings[i] = f"**{roll_strings[i]}**"
        else:
            for i, die in enumerate(rolls):
                if success_op(die, s_cond_val):
                    successes += 1
                    roll_strings[i] = f"**{roll_strings[i]}**"
        
        if match.groupdict()['failure_vals']:
            f_vals = [int(i) for i in info['failure_vals'].split('f')[1:]]
            failures = 0
            for i, die in enumerate(rolls):
                if die in f_vals:
                    failures += 1
                    roll_strings[i] = f"~~{roll_strings[i]}~~"
            return f"({' '.join(roll_strings)}, {successes} successes, {failures} failures)", successes - failures, None
        elif match.groupdict()['failure_cond']:
            failure_op = get_operator(info['failure_cond'])
            f_cond_val = int(info['failure_cond_val'])
            failures = 0
            for i, die in enumerate(rolls):
                if failure_op(die, f_cond_val):
                    failures += 1
                    roll_strings[i] = f"~~{roll_strings[i]}~~"
            print(f"Fails if die {match.groupdict()['failure_cond']} {match.groupdict()['failure_cond_val']}")
            return f"({' '.join(roll_strings)}, {successes} successes, {failures} failures)", successes - failures, None
        else:
            return f"({' '.join(roll_strings)}, {successes} successes)", successes, None
    print("Massive Error")
    return None, None, "Idk what happened, but something bad"
    

async def basic_roll(message):
    roll_string = r"(?P<num>[0-9]+)d(?P<dice>[0-9]+)"
    dice_roll = re.compile(rf"^{roll_string}$")
    match = dice_roll.match(message)
    count = False
    if not match:
        count, match = await check_count_dice(message, roll_string)
        if not count:
            return None, None, None
    command = match.groupdict()
    rolls = []
    max_dice = int(command['dice'])
    if max_dice == 0:
        return None, None, "Can't roll a d0"
    for i in range(int(command['num'])):
        rolls += [random.randint(1, max_dice)]
    if count:
        return await count_the_dice(message, roll_string, rolls)
    return f"({'+'.join(str(i) for i in rolls)})", sum(rolls), None

async def drop_dice(message):
    roll_string = r"^(?P<num>[0-9]+)d(?P<dice>[0-9]+)(?P<drop>k|kl|kh)(?P<keep_num>[0-9]+)$"
    dice_roll = re.compile(rf"^{roll_string}$")
    match = dice_roll.match(message)
    if not match:
        return None, None, None
    command = match.groupdict()
    rolls = []
    max_dice = int(command['dice'])
    if max_dice == 0:
        return None, None, "Can't roll a d0"
    for i in range(int(command['num'])):
        rolls += [random.randint(1, max_dice)]
    keep_num = int(command['keep_num'])
    if keep_num > int(command['num']):
        keep_num = command['num']
    if keep_num < 0:
        keep_num = 0
    if command['drop'] == 'kl':
        mask_rolls = [f'~~{i}~~' for i in rolls]
        cap = int(command['dice']) + 1
        for i in range(keep_num):
            m = numpy.argmin(rolls)
            mask_rolls[m] = rolls[m]
            rolls[m] = cap
        rolls = mask_rolls
        return f"({'+'.join(str(i) for i in rolls)})", sum([die for die in rolls if type(die)==int]), None
    else:
        mask_rolls = [f'~~{i}~~' for i in rolls]
        for i in range(keep_num):
            m = numpy.argmax(rolls)
            mask_rolls[m] = rolls[m]
            rolls[m] = 0
        rolls = mask_rolls
        return f"({'+'.join(str(i) for i in rolls)})", sum([die for die in rolls if type(die)==int]), None

async def explode_dice(message):
    roll_string = r"(?P<num>[0-9]+)d(?P<dice>[0-9]+)(!|(?P<explode_vals>(e[0-9]+)+)|e(?P<explode_cond>(<|>|<=|>=))(?P<cond_val>[0-9]+))"
    dice_roll = re.compile(rf"^{roll_string}$")
    match = dice_roll.match(message)

    count = False
    if not match:
        count, match = await check_count_dice(message, roll_string)
        if not count:
            return None, None, None
    command = match.groupdict()
    rolls = []
    max_dice = int(command['dice'])
    if max_dice == 0:
        return None, None, "Can't roll a d0"
    if max_dice == 1:
        return None, None, "Can't explode a d1"

    dice_to_roll = int(command['num'])
    if command['explode_vals']:
        # Targeted explode
        explode_vals = list(set([int(i) for i in command['explode_vals'].split('e')[1:]]))
        if len(explode_vals) == max_dice:
            return None, None, "Can't explode on every value"
        dice_rolled = 0
        while dice_to_roll > 0:
            if dice_rolled > dice_cutoff_num:
                return False, False, "Exploded too many times!"
            roll = random.randint(1, max_dice)
            rolls += [roll]
            if not roll in explode_vals:
                dice_to_roll -= 1
            dice_rolled += 1
    elif command['explode_cond']:
        # Conditional explode
        explode_cond = get_operator(command['explode_cond'])
        explode_cond_val = int(command['cond_val'])
        passes = False
        for i in range(1, max_dice+1):
            if not explode_cond(i, explode_cond_val):
                passes = True
                break
        if not passes:
            return False, False, "Can't explode on every value"
        dice_rolled = 0
        while dice_to_roll > 0:
            if dice_rolled > dice_cutoff_num:
                return False, False, "Exploded too many times!"
            roll = random.randint(1, max_dice)
            rolls += [roll]
            if not explode_cond(roll, explode_cond_val):
                dice_to_roll -= 1
            dice_rolled += 1
    else:
        # Base explode
        print("explode")
        dice_to_roll = int(command['num'])
        while dice_to_roll > 0:
            roll = random.randint(1, max_dice)
            rolls += [roll]
            if not roll == max_dice:
                dice_to_roll -= 1
        
    if count:
        return await count_the_dice(message, roll_string, rolls)
    return f"({'+'.join(str(i) for i in rolls)})", sum(rolls), None

async def reroll_dice(message):
    roll_string = r"(?P<num>[0-9]+)d(?P<dice>[0-9]+)((?P<reroll_vals>(r[0-9]+)+)|r(?P<reroll_cond>(<|>|<=|>=))(?P<cond_val>[0-9]+))"
    dice_roll = re.compile(rf"^{roll_string}$")
    match = dice_roll.match(message)
    # count = False
    if not match:
        # count, match = await check_count_dice(message, roll_string)
        # if not count:
        return None, None, None
    print("matched reroll")

    command = match.groupdict()
    rolls = []
    roll_strings = []
    max_dice = int(command['dice'])
    if max_dice == 0:
        return None, None, "Can't roll a d0"

    if command['reroll_vals']:
        print("targeted reroll")
        reroll_vals = list(set([int(i) for i in command['reroll_vals'].split('r')[1:]]))
        print("reroll_vals", reroll_vals)
        
        for i in range(int(command['num'])):
            roll = random.randint(1, max_dice)
            rolls += [roll]
            roll_strings += [str(roll)]

        print("rolls", rolls)
        new_rolls = []
        new_roll_strings = []

        for i, roll in enumerate(rolls):
            if roll in reroll_vals:
                new_roll = random.randint(1, max_dice)
                rolls[i] = new_roll
                roll_strings[i] = f"~~{roll_strings[i]}~~"
                new_roll_strings += [str(new_roll)]

        roll_strings += new_roll_strings
        print("rolls", rolls)
        print("rollstrings", roll_strings)

    if command['reroll_cond']:
        print("conditional reroll")
        reroll_cond = get_operator(command['reroll_cond'])
        reroll_cond_val = int(command['cond_val'])

        for i in range(int(command['num'])):
            roll = random.randint(1, max_dice)
            rolls += [roll]
            roll_strings += [str(roll)]

        print("rolls", rolls)
        new_rolls = []
        new_roll_strings = []

        for i, roll in enumerate(rolls):
            if reroll_cond(roll, reroll_cond_val):
                new_roll = random.randint(1, max_dice)
                rolls[i] = new_roll
                roll_strings[i] = f"~~{roll_strings[i]}~~"
                new_roll_strings += [str(new_roll)]

        roll_strings += new_roll_strings
        print("rolls", rolls)

    # if count:
        # return await count_the_dice(message, roll_string, rolls)
    return f"({'+'.join(str(i) for i in roll_strings)})", sum(rolls), None

async def fate_roll(message):
    roll_string = r"(?P<num>[0-9]+)dF"
    dice_roll = re.compile(rf"^{roll_string}$")
    match = dice_roll.match(message)
    if not match:
        return None, None, None
    symbols = ['-', 'b', '+']
    command = match.groupdict()
    rolls = []
    total = 0
    for i in range(int(command['num'])):
        r = random.randint(-1, 1)
        total += r
        rolls += [symbols[r+1]]
    return f"({''.join(str(i) for i in rolls)})", total, None

async def just_an_int(message):
    roll_string = r"-?[0-9]+"
    dice_roll = re.compile(rf"^{roll_string}$")
    match = dice_roll.match(message)
    if not match:
        return None, None, None
    return message, int(message), None

async def just_a_float(message):
    roll_string = r"-?[0-9]+.[0-9]+"
    dice_roll = re.compile(rf"^{roll_string}$")
    match = dice_roll.match(message)
    if not match:
        return None, None, None
    return message, float(message), None


options = [
    basic_roll,
    drop_dice,
    explode_dice,
    reroll_dice,
    fate_roll,
    just_an_int,
    just_a_float
]
count_suffix = r"(?P<operator>>|<|>=|<=|=)(?P<comp_num>[0-9]+)((?P<twice_vals>(t[0-9]+)+)|t(?P<twice_cond><|>|<=|>=)(?P<twice_cond_val>[0-9]+))?((?P<failure_vals>(f[0-9]+)+)|f(?P<failure_cond><|>|<=|>=)(?P<failure_cond_val>[0-9]+))?"
