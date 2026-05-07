def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = (None, -10**18)
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not free(nx, ny):
            continue

        onto = 0
        best_res = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < best_res:
                best_res = d
            if nx == rx and ny == ry:
                onto = 1

        d_op = cheb(nx, ny, ox, oy)
        # Prefer immediate collection, then reducing distance to closest resource,
        # while avoiding getting too close to the opponent.
        score = (30 if onto else 0) + (8 / (1 + best_res)) + (1.8 if d_op >= 3 else 0) - (1.2 if d_op <= 1 else 0) + (0.25 * d_op)

        if score > best[1]:
            best = ((dxm, dym), score)
        elif score == best[1] and best[0] is not None:
            if (dxm, dym) < best[0]:
                best = ((dxm, dym), score)

    return [best[0][0], best[0][1]] if best[0] is not None else [0, 0]