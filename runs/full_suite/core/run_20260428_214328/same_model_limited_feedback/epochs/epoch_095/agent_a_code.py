def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    res = observation.get("resources", [])
    obs = {(p[0], p[1]) for p in obstacles}

    moves = [(0, 0), (0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    def best_to_target(tx, ty):
        if not res:
            return man(sx + tx, sy + ty, ox, oy)
        best = None
        for rx, ry in res:
            d = man(sx + tx, sy + ty, rx, ry)
            if best is None or d < best:
                best = d
        return best

    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if res:
            d = best_to_target(dx, dy)
        else:
            d = man(nx, ny, ox, oy)
        scored.append((d, dx, dy))

    if not scored:
        return [0, 0]
    scored.sort(key=lambda t: (t[0], t[1], t[2]))
    return [scored[0][1], scored[0][2]]