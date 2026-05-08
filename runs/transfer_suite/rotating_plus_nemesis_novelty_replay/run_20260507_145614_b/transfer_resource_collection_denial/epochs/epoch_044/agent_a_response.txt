def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, x, y):
        dx = a - x
        if dx < 0:
            dx = -dx
        dy = b - y
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        return [0 if sx == tx else (1 if tx > sx else -1), 0 if sy == ty else (1 if ty > sy else -1)]

    if (sx, sy) in [tuple(r) for r in resources]:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = 0
        # Primary: maximize competitive advantage over resources.
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd == 0:
                val += 1000000
            else:
                val += (opd - myd) * 1000 - myd
        # Secondary: avoid giving opponent an immediate pickup this turn.
        opp_threat = 0
        for rx, ry in resources:
            if cheb(ox, oy, rx, ry) == 0:
                opp_threat += 1
            elif cheb(nx, ny, rx, ry) == 1 and cheb(ox, oy, rx, ry) == 1:
                opp_threat += 1
        val -= opp_threat * 200
        # Tertiary: encourage movement if values tie.
        if dx == 0 and dy == 0:
            val -= 1
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move