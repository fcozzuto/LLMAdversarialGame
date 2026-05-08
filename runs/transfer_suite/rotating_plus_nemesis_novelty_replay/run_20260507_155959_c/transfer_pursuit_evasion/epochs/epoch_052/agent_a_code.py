def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    sr = (observation.get("self_role", "") or "").lower()
    pr = ("purs" in sr) or ("hunter" in sr) or ("catch" in sr)
    is_evader = not pr

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_key = None

    def border_penalty(x, y):
        return min(x, w - 1 - x) + min(y, h - 1 - y)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)

        # tie-break: deterministic, prefers safer/legal and directionally useful moves
        if pr:
            # pursuer: get closer; avoid edges slightly
            edge = border_penalty(nx, ny)
            align = 0
            if (nx - ox == 0) or (ny - oy == 0):
                align = 1
            key = (d, -edge, align, dx, dy)
            better = best_key is None or key < best_key
        else:
            # evader: increase distance; avoid becoming aligned with pursuer and cling to edges less
            edge = border_penalty(nx, ny)
            align = 0
            if (nx - ox == 0) or (ny - oy == 0) or (abs(nx - ox) == abs(ny - oy) and nx != ox and ny != oy):
                align = 1
            key = (-d, edge, align, -dx, -dy)
            better = best_key is None or key < best_key

        if better:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]