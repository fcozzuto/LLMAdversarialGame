def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    res_list = observation.get("resources") or []
    resources = set()
    for p in res_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.add((p[0], p[1]))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    best = (None, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = 0
        if (nx, ny) in resources:
            score += 10**6
        score -= (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if dx == 0 and dy == 0:
            score -= 5
        if score > best[1]:
            best = ((dx, dy), score)
    if best[0] is None:
        return [0, 0]
    return [best[0][0], best[0][1]]