def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obs_pen(x, y):
        pen = 0
        for ix in (-1, 0, 1):
            for iy in (-1, 0, 1):
                if (x + ix, y + iy) in obstacles:
                    pen += 1
        return pen

    if not resources:
        return [0, 0]

    best = None
    for r in resources:
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        lead = opd - myd
        val = (lead, -myd, -obs_pen(rx, ry))
        if best is None or val > best[0]:
            best = (val, rx, ry)
    _, tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    curd = dist(sx, sy, tx, ty)
    bestm = None
    for dx, dy, nx, ny in moves:
        nd = dist(nx, ny, tx, ty)
        # If we're not the earliest, still try to get in a better lane (reduce opponent's options)
        steal_block = 0
        if resources:
            # local proxy: whether moving closer also moves away from opponent toward same target
            steal_block = dist(ox, oy, tx, ty) - dist(ox, oy, nx, ny)
        score = (curd - nd, steal_block, -obs_pen(nx, ny), -(abs(tx - nx) + abs(ty - ny)))
        if bestm is None or score > bestm[0]:
            bestm = (score, dx, dy)

    return [bestm[1], bestm[2]]