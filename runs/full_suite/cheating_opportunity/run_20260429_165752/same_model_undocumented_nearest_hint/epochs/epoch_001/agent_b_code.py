def choose_move(observation):
    W = observation["grid_width"]
    H = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    blocked = lambda x, y: x < 0 or y < 0 or x >= W or y >= H or (x, y) in obstacles

    # If no resources, drift toward center.
    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [0, 0] if blocked(nx, ny) else [dx, dy]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Prefer resources where we're closer than opponent.
        key = (do - ds, -ds, -((rx + ry) % 3))  # deterministic tie-break
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    (_, (tx, ty)) = best

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Deterministic ordering: diagonals then cardinals then stay
    moves.sort(key=lambda m: (m[0] == 0 or m[1] == 0, 1 if (m[0] == 0 and m[1] == 0) else 0))

    cur_d = dist((sx, sy), (tx, ty))
    best_m = (0, 0)
    best_improve = -10**9
    best_newd = 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        nd = dist((nx, ny), (tx, ty))
        improve = cur_d - nd
        # If equal improvement, prefer smaller remaining distance; then deterministic tie by position.
        if improve > best_improve or (improve == best_improve and (nd < best_newd or (nd == best_newd and (nx, ny) < (sx + best_m[0], sy + best_m[1])))):
            best_improve = improve
            best_newd = nd
            best_m = (dx, dy)

    # If all moves blocked, stay.
    nx, ny = sx + best_m[0], sy + best_m[1]
    if blocked(nx, ny):
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]