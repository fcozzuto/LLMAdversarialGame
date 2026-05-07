def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set((p[0], p[1]) for p in obstacles if p is not None)

    def kdist(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    my_best_key = None
    target = resources[0]
    for rx, ry in resources:
        my_d = kdist(sx, sy, rx, ry)
        op_d = kdist(ox, oy, rx, ry)
        # Prefer resources where we are (or become) closer than opponent; then closer overall
        key = (-(op_d - my_d), my_d, rx, ry)  # minimize first component => maximize (op_d-my_d)
        if my_best_key is None or key < my_best_key:
            my_best_key = key
            target = [rx, ry]
    tx, ty = target

    cur_my = kdist(sx, sy, tx, ty)
    cur_op = kdist(ox, oy, tx, ty)

    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        my_next = kdist(nx, ny, tx, ty)
        op_next = kdist(ox, oy, tx, ty)
        # Score move by improving our lead; tie-break by faster collection and safety (avoid edge/obstacle)
        lead_gain = (cur_op - cur_my) - (op_next - my_next)
        edge_pen = (nx == 0) + (nx == w - 1) + (ny == 0) + (ny == h - 1)
        key = (-lead_gain, my_next, edge_pen, tx, ty, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    if best_key is not None:
        return best_move

    # Fallback if all neighbors blocked: stay
    return [0, 0]