def choose_move(observation):
    self_pos = observation["self_position"]
    opp_pos = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    w = observation["grid_width"]
    h = observation["grid_height"]

    ox = {tuple(o) for o in obstacles}
    sx, sy = self_pos
    ax, ay = opp_pos

    if not resources:
        # No resources: drift toward opponent's side while avoiding obstacles
        cx = (w - 1) // 2
        cy = (h - 1) // 2
        tx, ty = cx, cy
    else:
        def dsq(p, q):
            dx = p[0] - q[0]
            dy = p[1] - q[1]
            return dx * dx + dy * dy

        # Choose resource where we are relatively closest to improve chance of securing it
        best = None
        best_val = None
        for r in resources:
            rv = tuple(r)
            if rv in ox:
                continue
            d_self = dsq((sx, sy), rv)
            d_opp = dsq((ax, ay), rv)
            # Prefer resources we are closer to; break ties by absolute closeness
            val = (d_self - d_opp, d_self, d_opp, rv[0], rv[1])
            if best_val is None or val < best_val:
                best_val = val
                best = rv
        tx, ty = best if best is not None else resources[0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in ox:
            continue
        d_target = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        d_opp = (nx - ax) * (nx - ax) + (ny - ay) * (ny - ay)
        # If possible, also prefer stepping toward the target in the direction of the resource
        step_align = (0 if tx == sx else (1 if nx - sx == (1 if tx > sx else -1) else 0)) + (0 if ty == sy else (1 if ny - sy == (1 if ty > sy else -1) else 0))
        score = (d_target, -d_opp, -step_align, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]