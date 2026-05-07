def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles or not inb(x, y)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        v = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources we are closer to; use margin, then our distance.
            margin = od - sd
            cur = margin * 100 - sd
            if cur > v:
                v = cur
        # Small bias to reduce being stuck near obstacles: prefer moves that reduce distance to some resource.
        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best