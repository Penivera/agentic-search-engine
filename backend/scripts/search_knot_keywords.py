import requests

BASE = "https://ase-f1e2b8fd.fastapicloud.dev"
QUERIES = [
    "solana wallet for ai agents",
    "jupiter token swap",
    "meteora dlmm liquidity",
    "kalshi prediction market trading",
    "ai agent wallet",
    "spending policy limits wallet",
    "hold and transfer spl tokens",
    "non-custodial autonomous wallet",
]

for query in QUERIES:
    response = requests.get(
        f"{BASE}/api/search/",
        params={"query": query, "top_k": 5},
        timeout=30,
    )
    print(f"\nQUERY: {query}")
    print("STATUS", response.status_code)
    if response.status_code != 200:
        print(response.text[:200])
        continue

    rows = response.json()
    if not rows:
        print("NO_RESULTS")
        continue

    top = rows[0]
    print("TOP_PLATFORM", top.get("platform_name"))
    print("TOP_SIM", round(float(top.get("similarity", 0.0)), 4))
    print("TOP_SKILL", top.get("skill_name"))
