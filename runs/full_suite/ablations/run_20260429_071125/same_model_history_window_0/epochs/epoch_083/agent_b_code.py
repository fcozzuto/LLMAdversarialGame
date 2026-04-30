def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose target resource with best advantage (opp farther than us).
    best = None
    for r in resources:
        rx, ry = r
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        adv = od - sd
        key = (adv, -sd, rx + ry)  # deterministic tie-break
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    target = best[1]

    tx, ty = target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic re-order preference: reduce dx first, then dy.
    dx_dir = 0 if tx == sx else (1 if tx > sx else -1)
    dy_dir = 0 if ty == sy else (1 if ty > sy else -1)
    preferred = []
    for mx, my in moves:
        if mx == dx_dir or my == dy_dir:
            preferred.append((mx, my))
    rest = [m for m in moves if m not in preferred]
    moves = preferred + rest

    # Score each move by moving closer to target, avoiding obstacles, and deprioritizing moving closer to opponent.
    best_move = [0, 0]
    best_score = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        sd2 = dist((nx, ny), (tx, ty))
        od2 = dist((nx, ny), (ox, oy))
        # If target is reached, prioritize immediately.
        reach_bonus = -1000 if sd2 == 0 else 0
        # Prefer moves that keep our advantage vs opponent on this target.
        self_adv = dist((ox, oy), (tx, ty)) - sd2
        score = (reach_bonus + self_adv * 10) + (-sd2) + (od2 * 0.1)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [mx, my]

    return [int(best_move[0]), int(best_move[1])]