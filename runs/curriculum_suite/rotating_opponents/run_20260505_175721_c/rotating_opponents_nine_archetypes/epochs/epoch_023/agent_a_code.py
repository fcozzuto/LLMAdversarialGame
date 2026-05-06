def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if resources:
        best = None
        for rx, ry in resources:
            st = cheb(sx, sy, rx, ry)
            ot = cheb(ox, oy, rx, ry)
            adv = ot - st
            cand = (-adv, st, rx, ry)
            if best is None or cand < best[0]:
                best = (cand, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        valid = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                valid.append((dx, dy, nx, ny))

    bestm = None
    for dx, dy, nx, ny in valid:
        d = cheb(nx, ny, tx, ty)
        opp_d = cheb(nx, ny, ox, oy)
        # Prefer progress; if tied, reduce opponent approach; deterministic tie by coords.
        cand = (d, -opp_d, dx, dy)
        if bestm is None or cand < bestm[0]:
            bestm = (cand, [dx, dy])
    return bestm[1]