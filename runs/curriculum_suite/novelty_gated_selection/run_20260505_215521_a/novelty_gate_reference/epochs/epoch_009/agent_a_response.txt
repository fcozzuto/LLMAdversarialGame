def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            s = -cheb(nx, ny, cx, cy) - 0.05 * cheb(nx, ny, ox, oy)
            if best is None or s > best[0]:
                best = (s, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    tx, ty = min(resources, key=lambda p: (cheb(ox, oy, p[0], p[1]), p[0], p[1]))

    # Opponent's likely next move: greedy toward target
    def opp_next_pos():
        best = None
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            key = (d, dx, dy, nx, ny)
            if best is None or key < best[0]:
                best = (key, nx, ny)
        return (ox, oy) if best is None else (best[1], best[2])

    nox, noy = opp_next_pos()
    opp_new_dist = cheb(nox, noy, tx, ty)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        our_dist = cheb(nx, ny, tx, ty)
        score = (opp_new_dist * 0.9) - our_dist
        if (nx, ny) == (tx, ty):
            score += 1000
        # If multiple resources are near target, slightly prefer reducing distance to current pool
        if resources:
            near_pool = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            score += -0.02 * near_pool
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]] if best else [0, 0]