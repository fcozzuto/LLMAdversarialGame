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
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Target: pick resource where we arrive earlier with largest margin; if none, head to nearest.
    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds
            key = (margin, -ds, -(abs(rx - ox) + abs(ry - oy)))
            if best is None or key > best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (0, 0) if ((ox + oy) & 1) == 0 else (w - 1, h - 1)

    # Choose move that reduces distance to target, avoids obstacles, deterministic tie-break.
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    order = {(-1, -1): 0, (-1, 0): 1, (-1, 1): 2, (0, -1): 3, (0, 0): 4, (0, 1): 5, (1, -1): 6, (1, 0): 7, (1, 1): 8}

    best_move = (0, 0)
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dnew = cheb(nx, ny, tx, ty)
        # primary: minimize distance to target, secondary: maximize lead margin vs opponent, tertiary: deterministic order
        lead = cheb(ox, oy, tx, ty) - dnew
        val = ( -dnew, lead, -abs(nx - ox) - abs(ny - oy), -order[(dx, dy)] )
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]