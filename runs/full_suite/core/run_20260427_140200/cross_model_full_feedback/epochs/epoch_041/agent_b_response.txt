def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1,  0), (0,  0), (1,  0),
            (-1,  1), (0,  1), (1,  1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If resources exist, move toward closest resource, tie-break by keeping away from opponent
    if resources:
        best_move = (0, 0)
        best_score = None
        best_res = None
        for rx, ry in resources:
            d_me = dist((sx, sy), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))
            for dx, dy in dirs:
                nx, ny = sx + dx, sy + dy
                if not legal(nx, ny):
                    continue
                nd = dist((nx, ny), (rx, ry))
                oppd = dist((nx, ny), (ox, oy))
                score = -nd  # closer to resource is better
                # bias away from opponent
                if oppd < dist((sx, sy), (ox, oy)):
                    score += 1
                if best_score is None or score > best_score or (score == best_score and (nx, ny) < best_res):
                    best_score = score
                    best_move = (dx, dy)
                    best_res = (nx, ny)
        if best_move != (0, 0) or True:
            return [best_move[0], best_move[1]]

    # No resources or fallback: move to maximize distance from opponent, stay legal
    best = (-10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            d = dist((nx, ny), (ox, oy))
            if d > best[0] or (d == best[0] and (nx, ny) < (sx, sy)):
                best = (d, dx, dy)
    if best[1] is None:
        return [0, 0]
    return [best[1], best[2]]