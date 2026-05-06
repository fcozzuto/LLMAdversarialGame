def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    # Deterministic move order for tie-breaking (prefer diagonals)
    neigh = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    best_r = resources[0]
    best_v = -10**18
    for (rx, ry) in resources:
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        corner_bonus = 0
        if (sx <= 1 and sy <= 1) or (sx >= w - 2 and sy >= h - 2):
            corner_bonus = 1
        v = (opd - myd) * 20 - myd + corner_bonus
        # small deterministic nudge: favor lower y then lower x
        v += (-ry) * 0.001 + (-rx) * 0.000001
        if v > best_v:
            best_v = v
            best_r = (rx, ry)

    tx, ty = best_r

    # Pick best neighbor step toward target with greedy advantage vs opponent
    best_step = (0, 0)
    best_sv = -10**18
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (sx, sy):
            continue_score = -0.5  # discourage staying unless forced
        else:
            continue_score = 0.0

        myd = manh(nx, ny, tx, ty)
        opd = manh(ox, oy, tx, ty)
        # advantage to the chosen target; also add slight anti-blocking: prefer not moving into "opponent closer"
        opp_closer_pen = 0
        if myd > manh(sx, sy, tx, ty) and myd - manh(sx, sy, tx, ty) >= 1:
            opp_closer_pen = 2
        sv = (opd - myd) * 20 - myd + continue_score - opp_closer_pen
        # deterministic tie-break
        sv += (dx * 0.0001) + (dy * 0.00001)
        if sv > best_sv:
            best_sv = sv
            best_step = (dx, dy)

    dx, dy = best_step
    nx, ny = sx + dx, sy + dy
    if in_bounds(nx, ny) and (nx, ny) not in obstacles:
        return [dx, dy]
    return [0, 0]