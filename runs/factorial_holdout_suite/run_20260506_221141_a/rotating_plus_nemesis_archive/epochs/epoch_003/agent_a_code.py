def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = [tuple(p) for p in (observation.get("resources", []) or [])]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    # Target selection: chase resources where we are relatively closer, but also prefer
    # resources not in opponent's immediate sweep line (row/col alignment).
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        advantage = od - sd  # higher is better for us
        # If opponent is on/near same row or column, it likely sweeps there; discount.
        align_pen = 0
        if ry == oy or abs(ry - oy) == 1:
            align_pen += 2
        if rx == ox or abs(rx - ox) == 1:
            align_pen += 1
        # Slight bias toward nearer resources to avoid over-committing.
        near_bias = sd
        key = (-advantage + align_pen, near_bias, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    # Move selection: avoid obstacles and choose move maximizing (opponent distance - our distance)
    # while progressing toward target.
    best_move = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        our_d = man(nx, ny, tx, ty)
        opp_to_target = man(ox, oy, tx, ty)
        # Progress term: closer to target is good.
        prog = our_d
        # Combat term: if we move into a state where we are closer to the target than opponent,
        # it's good; otherwise less good.
        my_dist_to_target = man(nx, ny, tx, ty)
        opp_dist_to_target_now = opp_to_target
        swing = opp_dist_to_target_now - my_dist_to_target
        # Small penalty for moving away from target.
        key = (-swing, prog, man(nx, ny, tx, ty), nx, ny)
        if best_move is None or key < best_move[0]:
            best_move = (key, (dx, dy))

    if best_move is None:
        return [0, 0]
    return [best_move[1][0], best_move[1][1]]