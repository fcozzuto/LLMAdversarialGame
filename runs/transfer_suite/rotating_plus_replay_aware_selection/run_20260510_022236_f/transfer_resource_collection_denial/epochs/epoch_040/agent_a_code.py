def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        x, y = p
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    res = []
    for p in resources:
        x, y = p
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))
    res_set = set(res)

    if (sx, sy) in obs:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if res:
        target = None
        bestd = 10**9
        for x, y in res:
            d = cheb(sx, sy, x, y)
            if d < bestd or (d == bestd and (x < target[0] or (x == target[0] and y < target[1]))):
                bestd = d
                target = (x, y)
    else:
        target = (ox, oy)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        d = cheb(nx, ny, target[0], target[1])
        on_res = 1 if (nx, ny) in res_set else 0
        # maximize: prefer landing on resource, then smaller distance
        score = (-on_res, d, abs(dx), abs(dy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]