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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_pen(x, y):
        pen = 0
        for ix in (-1, 0, 1):
            for iy in (-1, 0, 1):
                if (x + ix, y + iy) in obstacles:
                    pen += 1
        return pen

    if not resources:
        return [0, 0]

    # Choose target resource where we can arrive first (or at least reduce opponent lead)
    best = None
    for r in resources:
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        lead = opd - myd
        val = (lead, -myd, -obs_pen(rx, ry))
        if best is None or val > best[0]:
            best = (val, rx, ry)
    _, tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            myd2 = cheb(nx, ny, tx, ty)
            opd2 = cheb(ox, oy, tx, ty)
            # If opponent is very ahead at this target, drift to a better local alternative:
            # reward moves that increase opponent distance relative to ours for the current target.
            rel = opd2 - myd2
            # Small bias toward avoiding obstacles and toward actually decreasing distance
            val = (rel, -myd2, -obs_pen(nx, ny), -(abs(tx - nx) + abs(ty - ny)))
            moves.append((val, dx, dy, nx, ny))

    if moves:
        moves.sort(reverse=True)
        return [int(moves[0][1]), int(moves[0][2])]

    return [0, 0]