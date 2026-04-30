def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    cx, cy = (w - 1) // 2, (h - 1) // 2

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def passable(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def score_pos(x, y):
        if resources:
            dmin = 10**9
            for r in resources:
                rx, ry = r if isinstance(r, (list, tuple)) else (r, 0)
                dmin = min(dmin, manh((x, y), (rx, ry)))
            dopp = manh((x, y), (ox, oy))
            return 1000 - 3 * dmin + dopp * 0.02
        dcent = manh((x, y), (cx, cy))
        dletter = manh((x, y), (ox, oy))
        return 1000 - dcent + 0.01 * dletter

    best_s = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue
        s = score_pos(nx, ny)
        if s > best_s:
            best_s = s
            best_move = (dx, dy)
        elif s == best_s:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]