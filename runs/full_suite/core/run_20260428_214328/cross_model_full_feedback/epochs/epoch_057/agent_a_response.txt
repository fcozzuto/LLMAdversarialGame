def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b, c, d):
        dx = a - c; dx = -dx if dx < 0 else dx
        dy = b - d; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w - 1 - ox, h - 1 - oy
        dx = tx - sx; dx = -1 if dx < 0 else (1 if dx > 0 else 0)
        dy = ty - sy; dy = -1 if dy < 0 else (1 if dy > 0 else 0)
        return [dx, dy]

    # Choose a resource we are relatively closer to (favor contesting)
    best_r = None
    best_key = None
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        key = (d_self - d_opp, d_self, -(rx + ry))  # lower is better
        if best_key is None or key < best_key:
            best_key, best_r = key, (rx, ry)

    rx, ry = best_r
    best_m = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        d_self2 = cheb(nx, ny, rx, ry)
        d_opp2 = cheb(ox, oy, rx, ry)
        # If opponent can reach quickly, prioritize increasing their effective slack by moving away from them
        # and still not making our progress worse.
        prog = d_self2
        opp_reach = d_opp2 - d_self2  # higher => we are further ahead
        # Tie-break by moving to increase our distance from opponent
        away = cheb(nx, ny, ox, oy)
        val = (prog, -opp_reach, -away, dx, dy)
        if best_val is None or val < best_val:
            best_val, best_m = val, (dx, dy)

    return [int(best_m[0]), int(best_m[1])]