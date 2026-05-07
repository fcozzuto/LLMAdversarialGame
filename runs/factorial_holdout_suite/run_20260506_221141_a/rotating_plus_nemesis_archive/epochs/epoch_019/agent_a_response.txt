def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res = observation["resources"] or []
    obs_list = observation["obstacles"] or []

    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not res:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Evaluate each move by best "race" target; then break ties deterministically by delta order.
    best_sc = -10**18
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        move_best = -10**18
        for rx, ry in res:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            # Aim to be at least as close as opponent; heavily reward immediate capture.
            # Small penalty for farther distance to prefer earlier pickups.
            immediate = 1 if (nx == rx and ny == ry) else 0
            # Estimate opponent moves after us by subtracting 1 from their distance.
            od_after = od - 1
            if od_after < 0:
                od_after = 0
            sc = (od_after - sd) * 1000 - sd + immediate * 100000
            if sc > move_best:
                move_best = sc

        # Prefer moves that also reduce worst-case (denial) risk: avoid getting "beaten" badly.
        # Use the best_sc among targets; then add a mild stability term to keep moving forward.
        stability = -(abs((nx - rx)) + abs((ny - ry))) if False else 0  # deterministic no-op
        total_sc = move_best + stability

        if total_sc > best_sc:
            best_sc = total_sc
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]