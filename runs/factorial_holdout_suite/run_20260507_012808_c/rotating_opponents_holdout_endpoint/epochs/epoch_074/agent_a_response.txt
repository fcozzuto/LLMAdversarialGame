def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
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

    # Choose a resource we can reach strictly earlier (positive margin), otherwise closest overall.
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        margin = od - sd  # >0 means we are closer or equal-wins earlier by cheb
        # Deterministic scoring: prioritize positive margin, then smaller travel time, then coordinate tie-break
        score = (1 if margin > 0 else 0, margin, -sd, -abs(rx - sx) - abs(ry - sy), -rx, -ry)
        if best is None or score > best[0]:
            best = (score, rx, ry)
    _, tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Obstacle-aware local adjustment: try up to 8 neighbors toward target, else stay.
    candidates = []
    for ndx in (-1, 0, 1):
        for ndy in (-1, 0, 1):
            if ndx == 0 and ndy == 0:
                continue
            nx, ny = sx + ndx, sy + ndy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                # Prefer moves that reduce Chebyshev distance to target; tie-break by direction preference.
                dist = cheb(nx, ny, tx, ty)
                orient = -abs(ndx - dx) - abs(ndy - dy)
                candidates.append((dist, orient, ndx, ndy))
    candidates.sort(key=lambda t: (t[0], -t[1], t[2], t[3]))
    if candidates:
        _, _, mx, my = candidates[0]
        return [int(mx), int(my)]

    return [0, 0]