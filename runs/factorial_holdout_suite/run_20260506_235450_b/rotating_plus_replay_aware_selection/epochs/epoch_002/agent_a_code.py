def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    if not resources:
        return [0, 0]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    best_target = None
    best_key = None
    # Key: prioritize resources closer to us, and further from opponent; slight bias to remaining resources
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        d_self = dist2((sx, sy), (rx, ry))
        d_opp = dist2((ox, oy), (rx, ry))
        # If opponent is already extremely close, prefer other targets deterministically
        key = (d_self - d_opp, d_self, d_opp, -rx, -ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd = dist2((nx, ny), (tx, ty))
        opd = dist2((ox, oy), (tx, ty))

        # Prefer decreasing our distance; and also avoid becoming clearly worse than opponent
        # Tie-breaker prefers moves that reduce Manhattan to target and avoid being "passed" diagonally.
        man = abs(nx - tx) + abs(ny - ty)
        risk = dist2((nx, ny), (ox, oy))  # higher means farther from opponent
        score = (myd, (myd - opd), man, -risk, -nx, -ny)
        candidates.append((score, (mx, my)))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda x: x[0])
    return [candidates[0][1][0], candidates[0][1][1]]