def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # Fallback: drift toward opponent's corner (deterministic)
        tx, ty = (w - 1, h - 1) if (sx, sy) != (w - 1, h - 1) else (0, 0)
        target = (tx, ty)
    else:
        best = None
        bestv = -10**9
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            v = (do - ds) * 10 - ds  # prioritize resources we can reach sooner
            if v > bestv:
                bestv = v
                best = (rx, ry)
        target = best

    tx, ty = target
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    bestm = (0, 0)
    beste = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        dist_t = cheb(nx, ny, tx, ty)
        dist_o = cheb(nx, ny, ox, oy)
        # Encourage going for target and "influence" by reducing opponent advantage; avoid near-collision
        v = -dist_t * 10 + (cheb(ox, oy, tx, ty) - dist_t) * 1.2
        if dist_o == 0:
            v -= 50
        elif dist_o == 1:
            v -= 12
        else:
            v -= max(0, 3 - dist_o) * 2
        # Small deterministic tie-break to reduce dithering
        v -= (dx * 0.01 + dy * 0.001)
        if v > beste:
            beste = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]