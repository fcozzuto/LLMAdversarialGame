def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    row_resources = [r for r in resources if r[1] == oy]
    if row_resources:
        opp_target = min(row_resources, key=lambda r: man(ox, oy, r[0], r[1]))
    else:
        opp_target = min(resources, key=lambda r: man(ox, oy, r[0], r[1]))
    tx, ty = opp_target[0], opp_target[1]

    best = (None, None)
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        lead_count = 0
        best_our_dist = 10**9
        opp_dist_to_target = man(ox, oy, tx, ty)

        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if sd < od:
                lead_count += 1
            if sd < best_our_dist:
                best_our_dist = sd

        # If we can't improve leads, directly try to slow the opponent's row-target
        # by moving toward its row (y) and x direction.
        slow_dir = 0
        if ny == oy:
            slow_dir = 0
        else:
            slow_dir = abs(ny - oy)  # smaller is better
        our_to_row_target = man(nx, ny, tx, ty)

        val = (lead_count, -slow_dir, -our_to_row_target, -opp_dist_to_target, -best_our_dist)
        if best[0] is None or val > best:
            best = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]