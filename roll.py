#!/usr/bin/python3
import roll_utils, sys
import asyncio


original = sys.stdout  
sys.stdout = None
result = asyncio.run(roll_utils.handle_dice(None, " ".join(sys.argv[1:])))
sys.stdout = original
print(result)
