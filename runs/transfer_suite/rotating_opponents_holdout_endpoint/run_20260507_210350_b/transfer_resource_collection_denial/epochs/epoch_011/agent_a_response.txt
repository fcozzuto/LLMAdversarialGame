def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"] if tuple(p) not in obstacles]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Heuristic target scoring: prioritize resources we can reach sooner than opponent.
    # Sweep-row opponent: bias toward keeping y different from its current y to reduce interception.
    def reach_dist(x1, y1, x2, y2):
        return abs(x2 - x1) + abs(y2 - y1)

    def target_score(tx, ty):
        ds = reach_dist(sx, sy, tx, ty)
        do = reach_dist(ox, oy, tx, ty)
        y_bias = abs(ty - oy) * 0.02  # slight bias away from opponent row
        return (ds - 1.05 * do) + y_bias

    # Pick best target
    best_t = None
    best_ts = None
    for (tx, ty) in resources:
        ts = target_score(tx, ty)
        if best_ts is None or ts < best_ts or (ts == best_ts and (tx, ty) < best_t):
            best_ts = ts
            best_t = (tx, ty)
    tx, ty = best_t

    # Choose best immediate move toward the target, while not giving opponent advantage too early.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds1 = reach_dist(nx, ny, tx, ty)
        do1 = reach_dist(ox, oy, tx, ty)  # opponent position unchanged this turn
        # Prefer moves that reduce our distance, and if tie, reduce opponent's relative pressure
        val = (ds1 - 1.05 * do1, abs(nx - tx) + abs(ny - ty), (nx, ny))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]