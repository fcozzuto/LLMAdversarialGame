def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    if any(rx == sx and ry == sy for rx, ry in resources):
        return [0, 0]

    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; break ties by absolute closeness.
        key = (od - sd, -sd, rx, ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                sd2 = cheb(nx, ny, tx, ty)
                od2 = cheb(ox, oy, tx, ty)
                # Maximize (self advantage) and progress to target; small bias to move only if needed.
                adv = (od2 - sd2)
                moves.append((adv, -sd2, -abs(dx) - abs(dy), dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(reverse=True)
    return [int(moves[0][3]), int(moves[0][4])]