def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            r = (int(p[0]), int(p[1]))
            if r not in obs:
                res.append(r)

    if not res:
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [int(dx), int(dy)]
        return [0, 0]

    def safe(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def md(x1, y1, x2, y2):
        d = abs(x1 - x2) + abs(y1 - y2)
        return d

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        my_best = 10**9
        op_best = 10**9
        for rx, ry in res:
            d1 = md(nx, ny, rx, ry)
            if d1 < my_best:
                my_best = d1
            d2 = md(ox, oy, rx, ry)
            if d2 < op_best:
                op_best = d2
        # Favor moves that get closer to resources, and avoid leaving the opponent a big advantage.
        score = -my_best + 0.15 * (op_best - md(nx, ny, res[0][0], res[0][1])) - 0.01 * (abs(dx) + abs(dy))
        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]