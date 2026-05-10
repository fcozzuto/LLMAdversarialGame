def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_raw:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources_raw = observation.get("resources", []) or []
    resources = []
    for p in resources_raw:
        if p and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if resources:
            bestd = 10**9
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if d < bestd:
                    bestd = d
            res_score = -bestd
        else:
            cx, cy = w // 2, h // 2
            res_score = -(abs(nx - cx) + abs(ny - cy))
        opp_d = abs(nx - ox) + abs(ny - oy)
        return 10 * res_score + 0.5 * opp_d

    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            v = score_cell(nx, ny)
            if v > bestv:
                bestv = v
                best = (dx, dy)
    return [int(best[0]), int(best[1])]