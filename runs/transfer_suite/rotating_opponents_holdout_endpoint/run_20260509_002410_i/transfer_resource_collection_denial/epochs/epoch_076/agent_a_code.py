def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    tr = int(observation.get("turns_remaining", 0))
    prefer_feasible = (tr % 3 != 0)

    prefer_dx = -1 if (sx + sy + tr) % 2 == 0 else 1  # deterministic slight directional bias
    best = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        feasible = (my_d <= op_d)
        penalty = 0 if (not prefer_feasible or feasible) else 1
        diff = my_d - op_d  # smaller is better
        tie = (abs((rx - 0.5 * (w - 1)) - prefer_dx)) + abs(ry - (h - 1) / 2.0)
        cand = (penalty, diff, my_d, tie, rx, ry)
        if best is None or cand < best[0]:
            best = (cand, (rx, ry))

    tx, ty = best[1]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = [0, 0]
    best_key = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx + dx
            ny = sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            on_res = 1 if (nx, ny) in set(resources) else 0
            key = (-on_res, d, abs(dx) + abs(dy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]

    return best_move