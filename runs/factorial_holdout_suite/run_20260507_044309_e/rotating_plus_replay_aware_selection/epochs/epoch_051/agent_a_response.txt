def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prioritize resources we can reach not later than opponent; break ties by closeness, then advantage.
            can = 0 if ds <= do else 1
            key = (can, ds, - (do - ds))
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = w // 2, h // 2

    best_step = None
    best_k = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        # Keep moving toward target, but also prefer reducing opponent advantage.
        d_opp = cheb(ox, oy, tx, ty)
        k = (d_self, - (d_opp - d_self), abs(nx - tx) + abs(ny - ty))
        if best_k is None or k < best_k:
            best_k = k
            best_step = (dx, dy)

    return list(best_step if best_step is not None else (0, 0))