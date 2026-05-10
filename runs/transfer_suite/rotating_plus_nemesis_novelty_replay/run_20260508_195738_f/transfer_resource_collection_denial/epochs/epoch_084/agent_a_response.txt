def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    resources = []
    for r in (observation.get("resources", []) or []):
        try:
            resources.append((int(r[0]), int(r[1])))
        except Exception:
            pass

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (0, 0) if ((ox + oy) & 1) == 0 else (w - 1, h - 1)
    else:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # maximize our "lead slack" and closeness; also bias away from farthest resources
            key = (do - ds, -ds, -(abs(rx - ox) + abs(ry - oy)))
            if best is None or key > best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def safe(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        # Prefer reducing Chebyshev distance to target; lightly penalize moving away from center line to reduce dithering.
        dist = cheb(nx, ny, tx, ty)
        step_opp = cheb(nx, ny, ox, oy)
        val = (-dist, -step_opp, -abs(tx - ox) - abs(ty - oy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]