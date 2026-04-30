def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    def dist(a, b):  # squared euclidean
        dx = a[0] - b[0]; dy = a[1] - b[1]
        return dx * dx + dy * dy
    # Pick a target resource where we are relatively closer than opponent
    best = None
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        score = (ds - do)  # smaller => we are closer
        # small secondary: closer overall
        if best is None or score < best[0] or (score == best[0] and ds < best[1]):
            best = (score, ds, rx, ry)
    if best is None:
        # No resources: head toward opponent to contest space
        tx, ty = ox, oy
    else:
        tx, ty = best[2], best[3]

    moves = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx = sx + dx; ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    # If all blocked (shouldn't happen), stay
    if not moves:
        return [0, 0]

    # Choose move that reduces distance to target; add slight repulsion from opponent
    best_move = None
    best_val = None
    for dx, dy in moves:
        nx = sx + dx; ny = sy + dy
        d_target = dist((nx, ny), (tx, ty))
        d_opp = dist((nx, ny), (ox, oy))
        # Prefer being closer to target, and farther from opponent (deterministic)
        val = (d_target, -d_opp, abs(dx) + abs(dy))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]