def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Determine best target resource: closest to us; if tie, prefer far from opponent
    best = None
    best_key = None
    for r in resources:
        r = (r[0], r[1])
        if r in obstacles:
            continue
        d1 = dist((sx, sy), r)
        d2 = dist((ox, oy), r)
        key = (d1, -d2, r[0], r[1])
        if best is None or key < best_key:
            best = r
            best_key = key

    # If no resources, head to center
    if best is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic move ordering bias toward decreasing distance, with tie-breaks for stability
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_target = dist((nx, ny), (tx, ty))
        # Also consider avoiding moving closer to opponent too much (helps denial slightly)
        d_opp = dist((nx, ny), (ox, oy))
        mkey = (d_to_target, -d_opp, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    # If everything is blocked, engine will keep us; still must return valid delta
    return [int(best_move[0]), int(best_move[1])]