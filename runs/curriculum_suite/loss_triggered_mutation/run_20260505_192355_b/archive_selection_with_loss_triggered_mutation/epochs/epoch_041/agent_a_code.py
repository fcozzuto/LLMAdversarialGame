def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not free(sx, sy):
        for dx, dy in moves:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    best_move = (10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        score = 0
        if res:
            my_best = 10**9
            opp_best = 10**9
            for rx, ry in res:
                if (rx, ry) in obst:
                    continue
                my_best = min(my_best, abs(nx - rx) + abs(ny - ry))
                opp_best = min(opp_best, abs(ox - rx) + abs(oy - ry))
            # Prefer moves that reduce our distance to nearest resource, especially if we beat opponent.
            score = 2000 * (opp_best - my_best) - my_best
        # Small tie-break: avoid getting closer to opponent if resources absent or equal
        score -= 2 * dist((nx, ny), (ox, oy))
        if score > best_move[0]:
            best_move = (score, dx, dy)

    return [best_move[1], best_move[2]]