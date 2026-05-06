def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp(x, lo, hi):
        return lo if x < lo else (hi if x > hi else x)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # drift away from opponent to reduce contention
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
            if (nx, ny) in obs: 
                continue
            d = cheb(nx, ny, ox, oy)
            key = (d, -abs(nx - (w//2)), -abs(ny - (h//2)), dx, dy)
            if best is None or key > best[0]:
                best = (key, (dx, dy))
        return list(best[1]) if best else [0, 0]

    best_key = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obs:
            continue

        # evaluate move by the best resource swing it creates vs opponent
        best_res_key = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive means I can reach sooner
            key = (adv, -myd, opd, -rx, -ry)
            if best_res_key is None or key > best_res_key:
                best_res_key = key

        # also prefer moves that increase distance to opponent slightly (denial by pressure)
        opp_press = cheb(nx, ny, ox, oy)
        move_key = (best_res_key[0], best_res_key[1], best_res_key[2], opp_press, -abs(dx), -abs(dy), dx, dy)
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]