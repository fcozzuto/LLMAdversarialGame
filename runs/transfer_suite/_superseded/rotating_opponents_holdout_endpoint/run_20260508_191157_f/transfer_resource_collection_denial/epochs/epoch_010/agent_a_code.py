def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set(tuple(p) for p in obstacles)

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_move_towards(tx, ty):
        moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        best = (0, 0)
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs_set:
                continue
            self_to = man((nx, ny), (tx, ty))
            opp_to = man((ox, oy), (tx, ty))
            key = (opp_to - self_to, -self_to, -(dx * dx + dy * dy), nx, ny, -dx, -dy)
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return list(best)

    if not resources:
        return [0, 0]

    best_t = None
    best_key = None
    for r in resources:
        rx, ry = r
        sd = man((sx, sy), (rx, ry))
        od = man((ox, oy), (rx, ry))
        # Prefer resources we can reach no later than opponent; otherwise deny the largest advantage.
        win_bias = 1000 if sd <= od else 0
        key = (win_bias + (od - sd), -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = r

    tx, ty = best_t
    # If opponent is significantly closer, try to move into a nearer "handoff" square by steering toward the resource anyway,
    # but also allow a small deterministic detour to avoid getting stuck on obstacles.
    move = best_move_towards(tx, ty)

    # Safety: if chosen move is invalid due to an obstacle, try staying on the best legal neighbor.
    nx, ny = sx + move[0], sy + move[1]
    if (nx, ny) in obs_set or nx < 0 or nx >= w or ny < 0 or ny >= h:
        return [0, 0]
    return move