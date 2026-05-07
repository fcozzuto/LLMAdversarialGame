def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def d(a, b, c, e):
        return max(abs(c - a), abs(e - b))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        return [0, 0]

    ox, oy = observation["opponent_position"]
    res = [tuple(r) for r in resources]

    best_move = (None, -10**18, 10**9)  # move, score, self_dist
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate best resource we could likely secure from (nx, ny)
        local_best = (-10**18, 10**9)  # score, self_dist_to_that_resource
        for rx, ry in res:
            sd = d(nx, ny, rx, ry)
            od = d(ox, oy, rx, ry)
            # Positive means we're closer than opponent. Also bias toward immediate/near.
            score = (od - sd) * 1000 - sd
            if sd == 0:
                score += 50000  # strongly prefer collecting now if possible
            if score > local_best[0] or (score == local_best[0] and sd < local_best[1]):
                local_best = (score, sd)
        score, sd = local_best
        # Prefer higher score; break ties by being closer and then deterministic by move order
        if score > best_move[1] or (score == best_move[1] and sd < best_move[2]):
            best_move = ((dx, dy), score, sd)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0][0]), int(best_move[0][1])]