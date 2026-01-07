import sys
print(f"Python: {sys.version}")
try:
    import nest_asyncio
    print("nest_asyncio: Found")
except ImportError:
    print("nest_asyncio: MISSING")

try:
    import playwright
    print("playwright: Found")
except ImportError:
    print("playwright: MISSING")
