def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []
    op_t = observation.get("opponent_territory") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_set = {(x, y) for x, y in obstacles if inb(x, y)}
    un_list = [(x, y) for x, y in unclaimed if inb(x, y)]
    op_list = [(x, y) for x, y in op_t if inb(x, y)]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not un_list and not op_list:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if ax == cx else (1 if ax < cx else -1)
        dy = 0 if ay == cy else (1 if ay < cy else -1)
        return [dx, dy]

    targets = un_list if un_list else op_list
    # Choose a deterministic target: closest; tie by y then x.
    best_t = None
    best_key = None
    for (tx, ty) in targets:
        d = abs(tx - ax) + abs(ty - ay)
        key = (d, ty, tx)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)
    tx, ty = best_t

    # Prefer cutting toward target while not wasting moves into obstacles.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            score = 10**9
        else:
            nd = abs(tx - nx) + abs(ty - ny)
            # Small directional bias to avoid oscillation: prefer horizontal/vertical progress first.
            prog = (abs(tx - ax) + abs(ty - ay)) - nd
            score = nd - 0.01 * prog
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]