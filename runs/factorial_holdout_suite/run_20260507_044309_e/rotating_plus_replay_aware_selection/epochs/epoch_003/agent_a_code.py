def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer: larger time advantage for self (ds-do smaller), then smaller ds, then closer to center, then coord order
            key = (ds - do, ds, abs(rx - w // 2) + abs(ry - h // 2), rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1] if best else (w // 2, h // 2)

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]
    for mx, my in moves:
        if mx == 0 and my == 0:
            continue
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [mx, my]

    # If blocked, pick any legal move that reduces chebyshev distance to target; deterministic tie-break by move order
    bestm = (10**9, 0, 0)
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, tx, ty)
            key = (d, abs(mx) + abs(my), mx, my)
            if key < bestm:
                bestm = key
    return [bestm[2], bestm[3]]