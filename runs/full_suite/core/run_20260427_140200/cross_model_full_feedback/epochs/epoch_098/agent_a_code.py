def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    if res:
        targets = res[:]
        for i, t in enumerate(targets):
            pass  # no-op to keep deterministic ordering if res is not ordered

        for dx, dy in dirs:
            nx, ny = mx + dx, my + dy
            if not valid(nx, ny):
                continue
            cur = (nx, ny)
            # Prefer cells that reduce distance to a resource more than the opponent does.
            score = -10**9
            for rx, ry in targets:
                dm = man(cur, (rx, ry))
                do = man((ox, oy), (rx, ry))
                # Lower dm and higher margin over opponent is better.
                val = -dm + 0.6 * (do - dm)
                score = max(score, val)
            # Small tie-breaker: avoid getting adjacent to opponent
            opp_adj = (abs(nx - ox) + abs(ny - oy))
            val2 = score - 0.02 * opp_adj
            if val2 > best_val:
                best_val = val2
                best_move = (dx, dy)
    else:
        for dx, dy in dirs:
            nx, ny = mx + dx, my + dy
            if not valid(nx, ny):
                continue
            # Without resources, move to maximize distance from opponent.
            val = man((nx, ny), (ox, oy))
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    dx, dy = best_move
    if not (dx in (-1, 0, 1) and dy in (-1, 0, 1) and isinstance(dx, int) and isinstance(dy, int)):
        return [0, 0]
    return [dx, dy]