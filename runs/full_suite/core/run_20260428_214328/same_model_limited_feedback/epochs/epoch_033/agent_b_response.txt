def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose target resource with deterministic "advantage" vs opponent
    best = None  # (score, tx, ty)
    for tx, ty in resources:
        self_d = abs(tx - sx) + abs(ty - sy)
        opp_d = abs(tx - ox) + abs(ty - oy)
        # Advantage score: prefer resources opponent is less likely to reach first
        score = (opp_d - self_d, -self_d, -((tx * 8 + ty) if w >= 8 else tx))
        if best is None or score > best[0]:
            best = (score, tx, ty)
    if best is None:
        return [0, 0]
    _, tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic step preference order around target
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    def valid_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            return False
        if (nx, ny) in obstacles:
            return False
        return True

    # Try preferred direct step(s) first (towards target)
    preferred = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == dx0 and dy == dy0:
                preferred.insert(0, (dx, dy))
            else:
                preferred.append((dx, dy))
    preferred = [p for p in preferred if valid_move(p[0], p[1])]

    def dist_after(dx, dy):
        nx, ny = sx + dx, sy + dy
        return abs(tx - nx) + abs(ty - ny)

    # Among valid moves, pick one that minimizes distance to target
    best_move = None
    best_dist = None
    for dx, dy in preferred + deltas:
        if not valid_move(dx, dy):
            continue
        d = dist_after(dx, dy)
        key = (d, abs((sx + dx) - ox) + abs((sy + dy) - oy), dx, dy)
        if best_move is None or key < best_move:
            best_move = key
            best_dist = d

    return [best_move[2], best_move[3]]