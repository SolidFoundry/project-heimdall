#!/usr/bin/env python3
# Test script to verify the calculate function is working correctly

import sys
sys.path.append('src')

from heimdall.api.endpoints.testing import MockTools
import asyncio

async def test_calculate():
    result = await MockTools.calculate("2 + 2 * 3")
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_calculate())