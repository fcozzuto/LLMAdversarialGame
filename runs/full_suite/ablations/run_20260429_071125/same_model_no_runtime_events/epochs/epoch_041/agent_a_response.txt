def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not valid(sx, sy):
        for dx, dy in dirs:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**9
    res_list = resources if resources else [( (w - 1) // 2, (h - 1) // 2 )]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Favor moves that let us arrive earlier to some resource than the opponent.
        # If none, head toward a good next resource and (secondarily) away from giving the opponent a closer one.
        my_best_diff = 10**9
        my_best_m = 10**9
        for tx, ty in res_list:
            myd = kdist(nx, ny, tx, ty)
            od = kdist(ox, oy, tx, ty)
            diff = myd - od  # negative is good for us
            if diff < my_best_diff or (diff == my_best_diff and myd < my_best_m):
                my_best_diff = diff
                my_best_m = myd

        # Secondary heuristic: keep safe and avoid "losing tempo" when close to opponent.
        opp_close = kdist(nx, ny, ox, oy)
        center_bias = -kdist(nx, ny, (w - 1) / 2.0, (h - 1) / 2.0)
        score = (-my_best_diff) * 100 - my_best_m * 2 + opp_close * 0.5 + center_bias

        # If resources exist, prefer moving toward the nearest resource when still behind.
        if resources and my_best_diff > 0:
            nearest = 10**9
            for tx, ty in resources:
                nearest = min(nearest, kdist(nx, ny, tx, ty))
            score -= nearest

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]