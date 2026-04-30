def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev

    # Pick a target resource where we are relatively closer than opponent
    best = None
    best_key = None
    for r in resources:
        rt = tuple(r)
        if rt in obstacles:
            continue
        myd = dist((sx, sy), rt)
        opd = dist((ox, oy), rt)
        key = (myd - opd, myd, rt[0], rt[1])
        if best_key is None or key < best_key:
            best_key = key
            best = rt
    if best is None:
        return [0, 0]

    tx, ty = best
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    # Score moves: prefer reducing distance to target, and increasing opponent distance
    best_move = (0, 0)
    best_score = None
    for dx, dy, nx, ny in moves:
        myd = dist((nx, ny), (tx, ty))
        opd = dist((ox, oy), (nx, ny))
        # also avoid moving into opponent's immediate neighborhood
        opp_close = 1 if dist((nx, ny), (ox, oy)) <= 1 else 0
        score = (opp_close, myd, -opd, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]