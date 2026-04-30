def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not valid(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        tx, ty = ox, oy
        best = (10**9, None)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = cheb(nx, ny, tx, ty)
            if score < best[0]:
                best = (score, (dx, dy))
        return list(best[1] or (0, 0))

    rc = len(resources)
    prefer_far = 2 if rc <= 6 else 1  # when resources scarce, avoid early “swaps” near opponent
    prefer_center = 0.08  # small tie-break to avoid dithering

    best_score = 10**18
    best_move = (0, 0)
    cX, cY = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # distance to closest resource (primary)
        dmin = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < dmin:
                dmin = d

        # discourage moving closer to opponent unless it also improves resource distance
        cur_do = cheb(sx, sy, ox, oy)
        new_do = cheb(nx, ny, ox, oy)
        opp_pen = 0
        if new_do < cur_do:
            opp_pen = (cur_do - new_do) * (1.2 + 0.3 * rc)
        else:
            opp_pen = 0.0 - (new_do - cur_do) * prefer_far

        # slight bias toward grid center for determinism/tie-breaking
        center_bias = (abs(nx - cX) + abs(ny - cY)) * prefer_center

        score = dmin * 10 + opp_pen + center_bias

        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]