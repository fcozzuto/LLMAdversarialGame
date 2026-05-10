def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []
    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    uset = {(p[0], p[1]) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    oset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    ucell = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def mindist_to_set(x, y, s):
        best = 10**9
        for px, py in s:
            d = (px - x) * (px - x) + (py - y) * (py - y)
            if d < best: best = d
        return best if s else best

    # Priority 1: immediate flip by stepping onto opponent territory.
    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obset:
            continue
        val = 0.0
        if (nx, ny) in oset:
            val += 10000.0 - ((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)) * 0.5
        elif (nx, ny) in ucell:
            # Claim unclaimed while moving toward center and away from opponent for safer expansion.
            val += 120.0 - ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 2.0
            val += ((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)) * 0.05
        else:
            # Prefer staying on our territory and drifting toward center.
            if (nx, ny) in uset:
                val += 20.0
            val += 40.0 - ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 1.5
            # If opponent is nearby, don't leak too much: slight penalty for approaching them unless it enables unclaimed.
            val -= ((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)) * -0.01

        # Small tie-break: deterministic preference order already embedded by iteration.
        if val > best_val:
            best_val = val
            best = (dx, dy)

    # If all moves invalid (unlikely), stay.
    if best_val == -10**18:
        return [0, 0]
    return [best[0], best[1]]