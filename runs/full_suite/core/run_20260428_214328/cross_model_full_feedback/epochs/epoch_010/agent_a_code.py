def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def is_blocked(x, y):
        return (x, y) in obstacles or (x, y) == (ox, oy) or not inside(x, y)

    best = None
    best_key = None

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if is_blocked(nx, ny):
                continue
            key = (cheb(nx, ny, ox, oy), -(dx * dx + dy * dy))
            if best_key is None or key > best_key:
                best_key = key
                best = [dx, dy]
        return best if best is not None else [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if is_blocked(nx, ny):
            continue

        on_res = 1 if (nx, ny) in set(tuple(r) for r in resources) else 0

        best_my = 10**9
        best_opp = 10**9
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            if d_my < best_my:
                best_my = d_my
                best_opp = cheb(ox, oy, rx, ry)

        key = (on_res, -best_my, -(best_opp <= best_my), -abs(ox - nx) - abs(oy - ny), -dx * dx - dy * dy)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]