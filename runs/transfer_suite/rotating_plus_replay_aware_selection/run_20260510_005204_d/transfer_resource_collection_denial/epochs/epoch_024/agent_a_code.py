def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obs_list)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    if not resources:
        return [0, 0]

    def opp_move_toward(rx, ry):
        best = (ox, oy)
        bestd = 10**18
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = ox, oy
            d = md(nx, ny, rx, ry)
            if d < bestd:
                bestd = d
                best = (nx, ny)
        return best

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        # Score by best resource under a greedy opponent response.
        score = -10**18
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            ax, ay = opp_move_toward(rx, ry)
            opd = md(ax, ay, rx, ry)
            # Prefer smaller my distance and larger opponent distance.
            v = (opd - myd)
            # Small deterministic center bias to break ties.
            cx = (w - 1) / 2.0
            cy = (h - 1) / 2.0
            v -= int(abs(rx - cx) + abs(ry - cy))
            if v > score:
                score = v
        if score > best_score:
            best_score = score
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]