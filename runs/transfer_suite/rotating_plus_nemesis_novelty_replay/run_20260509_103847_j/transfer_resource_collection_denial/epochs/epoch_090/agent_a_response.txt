def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(obstacles_list) if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    # Prefer resources where we are not behind the opponent; then go for nearest.
    best = None
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        behind = ds > do  # if opponent can reach first, likely denied
        adv = do - ds    # higher => we reach earlier
        if behind:
            # still allow if all else fails, but de-prioritize heavily
            key1 = 1
        else:
            key1 = 0
        # Also bias toward current opponent row/col to reduce denial success (row sweep style).
        row_bias = 1 if ry == oy else 0
        col_bias = 1 if rx == ox else 0
        key = (key1, -adv, ds, row_bias + col_bias)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(tx - ox) + abs(ty - oy)
        # Prefer reducing distance, and if we can keep advantage over opponent, prefer that.
        key = (d_self, abs(tx - nx) + abs(ty - ny), -(d_opp - d_self), (nx == ox and ny == oy))
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]