def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    defs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    def valid_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        return inb(nx, ny) and (nx, ny) not in obstacles

    best = None
    best_score = None

    for dx, dy in defs:
        if not valid_move(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        if resources:
            m = -10**18
            for rx, ry in resources:
                ds = dist(nx, ny, rx, ry)
                do = dist(ox, oy, rx, ry)
                v = (do - ds) * 100 - ds
                if v > m:
                    m = v
            s = m
        else:
            s = dist(nx, ny, ox, oy) * 100
        if best_score is None or s > best_score or (s == best_score and (dx, dy) < best):
            best_score = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]