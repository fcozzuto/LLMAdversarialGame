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

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
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

    best_move = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        v = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Try to reach resources where we can be earlier; if none, contest the least-lost one.
            # Also slightly prefer closer positions to avoid dithering.
            cand = (od - sd) * 10 - sd
            if cand > v:
                v = cand
        # Small deterministic tie-break: prefer moves that reduce distance to the best resource directly.
        if v > bestv:
            bestv = v
            best_move = [dx, dy]
    return best_move