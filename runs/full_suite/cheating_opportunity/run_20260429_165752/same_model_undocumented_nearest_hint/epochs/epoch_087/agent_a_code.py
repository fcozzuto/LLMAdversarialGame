def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    def score(nx, ny, tx, ty):
        d1 = abs(nx - tx)
        d2 = abs(ny - ty)
        dist = d1 if d1 > d2 else d2
        return dist

    targets = resources[:] if resources else [(W // 2, H // 2)]
    if not targets:
        targets = [(ox, oy)]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        tx, ty = targets[0]
        if resources:
            # choose nearest visible resource deterministically
            best_d = None
            for (rx, ry) in resources:
                d = score(nx, ny, rx, ry)
                if best_d is None or d < best_d or (d == best_d and (rx, ry) < (tx, ty)):
                    best_d = d
                    tx, ty = rx, ry
            val = best_d
        else:
            val = score(nx, ny, ox, oy)
        # tie-break by preferring moves closer to opponent, then lexicographic
        opp_d = score(nx, ny, ox, oy)
        cand = (val, opp_d, dx, dy)
        if best_val is None or cand < best_val:
            best_val = cand
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]