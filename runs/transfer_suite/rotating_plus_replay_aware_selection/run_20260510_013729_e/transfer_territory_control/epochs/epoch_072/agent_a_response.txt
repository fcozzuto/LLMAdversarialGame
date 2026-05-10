def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    x, y = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    if not unclaimed:
        return [0, 0]

    # Prefer interior cells to counter "territory_edge_claim"
    def interior_penalty(tx, ty):
        d = min(tx, w - 1 - tx, ty, h - 1 - ty)
        return -0.8 * d  # higher d => less negative => better

    # Use opponent distance to discourage stepping into their easy grabs
    opp_cells = observation.get("opponent_territory") or []
    opp_set = set((int(p[0]), int(p[1])) for p in opp_cells if isinstance(p, (list, tuple)) and len(p) >= 2)

    def nearest_opp_dist(tx, ty):
        if not opp_set:
            return abs(tx - ox) + abs(ty - oy)
        # crude bound: min over a small subset near opponent to stay fast
        best = 10**9
        # deterministic scan limited by intersection with local radius
        r = 3
        for px, py in opp_set:
            if abs(px - ox) <= r and abs(py - oy) <= r:
                d = abs(tx - px) + abs(ty - py)
                if d < best:
                    best = d
        return best if best != 10**9 else abs(tx - ox) + abs(ty - oy)

    # Deterministic target selection
    best_t = None
    best_s = -10**18
    for tx, ty in unclaimed:
        ds = abs(tx - x) + abs(ty - y)
        if ds == 0:
            s = 10**6
        else:
            dop = nearest_opp_dist(tx, ty)
            # Greedy: maximize (self progress) and (opponent separation), with interior bias
            s = (6.0 / (1 + ds)) + (0.25 * dop) + interior_penalty(tx, ty)
        # tie-breaker: lexicographic for determinism
        if s > best_s or (s == best_s and (tx, ty) < best_t):
            best_s = s
            best_t = (tx, ty)

    tx, ty = best_t
    dx_raw = 0 if tx == x else (1 if tx > x else -1)
    dy_raw = 0 if ty == y else (1 if ty > y else -1)

    # Try preferred move first; if blocked by obstacle or off-grid, try alternatives deterministically
    deltas = [
        [dx_raw, dy_raw],
        [dx_raw, 0],
        [0, dy_raw],
        [dx_raw, -dy_raw],
        [-dx_raw, dy_raw],
        [0, 0],
        [1 if tx > x else -1 if tx < x else 0, 1 if ty > y else -1 if ty < y else 0],
        [1 if tx > x else -1 if tx < x else 0, 0],
        [0, 1 if ty > y else -1 if ty < y else 0],
    ]
    # Normalize duplicates with fixed order by scanning and returning first valid
    for dx, dy in deltas:
        nx, ny = x + int(dx), y + int(dy)
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(dx), int(dy)]

    return [0, 0]