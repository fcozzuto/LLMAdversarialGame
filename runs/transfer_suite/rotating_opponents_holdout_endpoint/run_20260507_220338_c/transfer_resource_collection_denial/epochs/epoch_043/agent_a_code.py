def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx >= dy else dy

    res_list = [tuple(r) for r in resources if tuple(r) not in obstacles]
    if not res_list:
        return [0, 0]

    best = (0, 0)
    best_val = -10**18
    # Consider at most nearest resources to keep deterministic and fast
    res_list_sorted = sorted(res_list, key=lambda p: cheb(sx, sy, p[0], p[1]))
    res_list_sorted = res_list_sorted[:6]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        # Large reward if we move onto a resource now
        if (nx, ny) in res_list:
            val += 100000

        for rx, ry in res_list_sorted:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer taking resources where we are closer than opponent
            margin = opd - myd
            val += margin * 250
            # Penalize being far away
            val -= myd * 8

            # Extra shaping: if opponent is very close and we aren't, try to reduce their advantage
            if opd <= 1 and myd > opd:
                val -= (myd - opd) * 120

        # Deterministic tie-break: lexicographically smaller move
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]