def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set()
    for p in obstacles:
        if len(p) >= 2:
            obs.add((p[0], p[1]))

    def manh(a, b):
        return (a[0] - b[0]) if a[0] >= b[0] else (b[0] - a[0]) + ((a[1] - b[1]) if a[1] >= b[1] else (b[1] - a[1]))

    best_t = None
    best_d = None
    for r in resources:
        if len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        if best_t is None or manh((sx, sy), (rx, ry)) < best_d or (manh((sx, sy), (rx, ry)) == best_d and (rx, ry) < best_t):
            best_t = (rx, ry)
            best_d = manh((sx, sy), (rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp_xy(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def score(pos):
        x, y = pos
        if best_t is None:
            d_op = manh((x, y), (ox, oy))
            return d_op
        d_me = manh((x, y), best_t)
        d_op = manh((x, y), (ox, oy))
        return -2 * d_me + d_op

    best_move = (0, 0)
    best_score = None
    any_valid = False

    for dx, dy in moves:
        nx, ny = clamp_xy(sx + dx, sy + dy)
        if (nx, ny) in obs:
            continue
        any_valid = True
        sc = score((nx, ny))
        if best_score is None or sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    if not any_valid:
        nx, ny = clamp_xy(sx, sy)
        if (nx, ny) in obs:
            for dx, dy in moves:
                tx, ty = clamp_xy(sx + dx, sy + dy)
                if (tx, ty) not in obs:
                    return [dx, dy]
            return [0, 0]
        return [0, 0]

    return [best_move[0], best_move[1]]