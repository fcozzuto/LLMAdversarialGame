def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    moves.sort()
    def dist(a, b):  # Chebyshev for grid with diagonals
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    # Pick target resource: prioritize ones we are closer to than opponent, then closest.
    if resources:
        best = None
        for rx, ry in resources:
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            key = (ds - do, ds, rx, ry)  # deterministic
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (ox, oy)  # fallback: move toward opponent (rare)
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to = dist((nx, ny), (tx, ty))
        # Encourage blocking: if next move is closer to that target than opponent, boost it.
        opp_d = dist((ox, oy), (tx, ty))
        val = (d_to, (opp_d - d_to), abs(nx-ox)+abs(ny-oy), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]