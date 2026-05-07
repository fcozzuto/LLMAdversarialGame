def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dres = 10**9
        for rx, ry in res:
            dd = abs(rx - nx) + abs(ry - ny)
            if dd < dres:
                dres = dd
        dopp = abs(ox - nx) + abs(oy - ny)
        score = 0
        if dres != 10**9:
            score += 1000 - 10 * dres
        score += 5 * dopp
        if (nx, ny) in res:
            score += 10000
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return [int(best[0]), int(best[1])]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [int(dx), int(dy)]
    return [0, 0]