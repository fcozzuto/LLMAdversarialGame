def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
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

    def clamp_in(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick a resource where we are comparatively closer than opponent.
    best_r = None
    best_key = None
    for (rx, ry) in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # maximize (od - md), then minimize md, then fixed tie-break by coordinates
        key = (od - md, -md, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    # Choose best 1-step move toward target with obstacle safety and local spacing.
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if (0, 0) in deltas:
        deltas.remove((0, 0))
        deltas.append((0, 0))  # prefer moving unless equally good

    def min_obst_dist(nx, ny):
        m = 99
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                x2, y2 = nx + ddx, ny + ddy
                if (x2, y2) in obstacles:
                    m = 0
                elif 0 <= x2 < w and 0 <= y2 < h:
                    # approximate "nearness" using Chebyshev to nearest obstacle in 1-step neighborhood only
                    pass
        # if no adjacent obstacle, give small bonus
        return m

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_op = cheb(nx, ny, ox, oy)
        # Prefer shorter path to target, avoid giving opponent too much advantage.
        # Also lightly avoid being adjacent to obstacles.
        score = (-d_to_t * 10) + (d_to_op * 0.3) + (min_obst_dist(nx, ny) * 0.1)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (