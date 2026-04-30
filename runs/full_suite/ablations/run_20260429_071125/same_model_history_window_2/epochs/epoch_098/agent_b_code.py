def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    tx, ty = (ox, oy) if not resources else resources[0]
    if resources:
        # pick deterministic target: min cheb distance, tie by lex
        best_d = 10**18
        for (rx, ry) in resources:
            d = abs(sx - rx)
            e = abs(sy - ry)
            cheb = d if d > e else e
            if cheb < best_d or (cheb == best_d and (rx, ry) < (tx, ty)):
                best_d = cheb
                tx, ty = rx, ry
    else:
        # chase with slight preference toward farthest corner from opponent
        tx, ty = (w - 1, h - 1) if (abs(ox - (w - 1)) + abs(oy - (h - 1)) >= abs(ox - 0) + abs(oy - 0)) else (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # score: reduce distance to target; avoid moving into opponent's immediate zone
        dist = abs(nx - tx)
        dist2 = abs(ny - ty)
        cheb = dist if dist > dist2 else dist2
        opp_adj = max(abs(nx - ox), abs(ny - oy))
        val = -cheb * 1000 - opp_adj * 10
        # small reward if cell contains a resource
        if resources:
            if (nx, ny) in set(resources):
                val += 500000
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]