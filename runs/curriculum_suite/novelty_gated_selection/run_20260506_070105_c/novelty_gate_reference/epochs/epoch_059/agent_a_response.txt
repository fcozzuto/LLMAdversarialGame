def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
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

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = [0, 0]
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                v = (abs(nx - ox) + abs(ny - oy), abs(nx - (w // 2)) + abs(ny - (h // 2)), nx, ny)
                if bestv is None or v < bestv:
                    bestv = v
                    best = [dx, dy]
        return best

    best_target = None
    best_key = None
    for rx, ry in resources:
        st = md((sx, sy), (rx, ry))
        ot = md((ox, oy), (rx, ry))
        lead = ot - st
        key = (-lead, st, ot, rx, ry)  # maximize lead; then self fast; then opp fast; deterministic tie
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            st = abs(nx - rx) + abs(ny - ry)
            ot = abs(nx - ox) + abs(ny - oy)
            # also slightly prefer moving in the general direction of the target
            dir_bias = (0 if (rx - nx) == 0 else 1) + (0 if (ry - ny) == 0 else 1)
            cand.append(([dx, dy], (st, ot, dir_bias, nx, ny)))
    cand.sort(key=lambda t: t[1])
    return cand[0][0] if cand else [0, 0]