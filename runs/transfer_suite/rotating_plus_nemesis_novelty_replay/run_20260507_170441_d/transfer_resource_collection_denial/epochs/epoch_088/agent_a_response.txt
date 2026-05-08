def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    def dist8(x1, y1, x2, y2):
        ax = abs(x1 - x2)
        ay = abs(y1 - y2)
        return ax if ax > ay else ay

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick best target resource from our perspective (with opponent competition)
    best_target = None
    best_target_val = -10**18
    my_to_center = abs((w - 1) / 2 - sx) + abs((h - 1) / 2 - sy)
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d  # >0 means we are closer
        # Encourage taking a resource we can plausibly secure; otherwise still take something to start progress.
        v = adv * 1200 - my_d * 3 - my_to_center * 0.05
        if v > best_target_val:
            best_target_val = v
            best_target = (rx, ry)

    rx, ry = best_target
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy

        my_d = dist8(nx, ny, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d

        # Additional check: if there exists another resource where we gain immediate relative advantage, prefer it.
        # (Small set scoring: enough for deterministic improvement without full search.)
        secondary_gain = -10**9
        for (r2x, r2y) in resources:
            if r2x == rx and r2y == ry:
                continue
            my2 = dist8(nx, ny, r2x, r2y)
            op2 = dist8(ox, oy, r2x, r2y)
            secondary_gain = max(secondary_gain, (op2 - my2) * 900 - my2 * 1.5)

        sep = abs(nx - ox) + abs(ny - oy)
        center_bias = -(abs((w - 1) / 2 - nx) + abs((h - 1) / 2 - ny)) * 0.05

        val = adv * 1400 - my_d * 3.2 + center_bias + sep * 0.03 + max(0, secondary_gain) * 0.35
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]