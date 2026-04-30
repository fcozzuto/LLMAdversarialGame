def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((x, y) for x, y in obstacles)
    move_order = [(0,0), (1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    valid_moves = []
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacle_set:
            valid_moves.append((dx, dy))

    if not resources:
        # Drift toward opponent's side to avoid deadlocks
        tx = 7 if ox < sx else 0
        ty = 7 if oy < sy else 0
        best, bestv = (0,0), None
        for dx, dy in valid_moves:
            nx, ny = sx + dx, sy + dy
            v = dist((nx, ny), (tx, ty))
            if bestv is None or v < bestv or (v == bestv and (dx, dy) == best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Choose a target we can reach sooner than opponent (or closest if none)
    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        key = (ds - do, ds, rx, ry)  # more negative is better; then nearer
        if best_key is None or key < best_key:
            best_key, best_target = key, (rx, ry)

    tx, ty = best_target
    best_move = (0, 0)
    best_score = None
    d_opp = dist((ox, oy), (tx, ty))
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        ds_after = dist((nx, ny), (tx, ty))
        # Maximize (opponent distance advantage) and break ties by moving closer, then determinism
        score = (d_opp - ds_after, -ds_after, -abs(nx - ox) - abs(ny - oy), -dx, -dy)
        if best_score is None or score > best_score:
            best_score, best_move = score, (dx, dy)

    return [best_move[0], best_move[1]]