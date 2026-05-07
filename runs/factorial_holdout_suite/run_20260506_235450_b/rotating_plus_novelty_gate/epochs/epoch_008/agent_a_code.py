def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set((p[0], p[1]) for p in obstacles)

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Target: where we are relatively closest vs opponent (Manhattan).
    best = None
    for rx, ry in resources:
        my_d = md(sx, sy, rx, ry)
        op_d = md(ox, oy, rx, ry)
        # Strongly prefer being ahead; then being closer; then deterministic coordinate.
        key = (op_d - my_d, -my_d, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        my_next = md(nx, ny, tx, ty)
        op_now = md(ox, oy, tx, ty)
        adv_next = op_now - my_next

        # Also slightly encourage moving toward any resource if advantage ties.
        nearest_next = None
        for rx, ry in resources:
            d = md(nx, ny, rx, ry)
            if nearest_next is None or d < nearest_next:
                nearest_next = d

        key = (adv_next, -my_next, -nearest_next if nearest_next is not None else 0, -tx, -ty, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]