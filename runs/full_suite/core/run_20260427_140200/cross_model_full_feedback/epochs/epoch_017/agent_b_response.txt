def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is None or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    free = lambda x, y: inb(x, y) and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # If there are resources, bias toward nearest resource, with simple tie-breaks
    if resources:
        best = None  # (score, dx, dy)
        for dx, dy, nx, ny in cand:
            bestd = 10**9
            for tx, ty in resources:
                d = abs(tx - nx) + abs(ty - ny)
                if d < bestd:
                    bestd = d
            score = bestd
            if best is None or score < best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
                best = (score, dx, dy)
        if best is not None:
            return [int(best[1]), int(best[2])]

    # Otherwise, move toward opponent to pressure or block if in range
    best_move = None
    best_score = None
    for dx, dy, nx, ny in cand:
        d_to_opp = dist((nx, ny), (ox, oy))
        # Prefer positions that reduce distance to opponent
        score = d_to_opp
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)
    if best_move is not None:
        return [int(best_move[0]), int(best_move[1])]

    return [0, 0]