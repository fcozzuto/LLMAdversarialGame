def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        ax = dx if dx >= 0 else -dx
        ay = dy if dy >= 0 else -dy
        return ax if ax > ay else ay

    # If no resources, move to center-ish to reduce chance of being blocked
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            key = (d, abs((nx - sx) + (ny - sy)))
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)
        return list(best if best is not None else (0, 0))

    # Choose resource with strongest capture advantage: our_dist - 0.9*opp_dist (minimize)
    best_res = None
    best_key = None
    for rx, ry in resources:
        od = cheb(ox, oy, rx, ry)
        sd = cheb(sx, sy, rx, ry)
        # prioritize resources nearer to us, but especially those opponent can't reach as fast
        key = (sd - (9 * od) // 10, sd, (rx + ry) & 3, rx, ry)
        if best_key is None or key < best_key:
            best_key, best_res = key, (rx, ry)

    rx, ry = best_res
    # If already on a resource cell, stay (engine should count/allow pickup)
    if sx == rx and sy == ry:
        return [0, 0]

    # Greedy one-step move that keeps minimizing the same advantage metric
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        sd = cheb(nx, ny, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (sd - (9 * od) // 10, sd, nx - rx, ny - ry, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]