def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        # Choose best target deterministically (closest manhattan, then tie by coordinates)
        best = None
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    # If opponent is closer to the same target, try a secondary target to contest
    opp_closer = resources and (abs(tx - ox) + abs(ty - oy) < abs(tx - sx) + abs(ty - sy))
    if opp_closer and len(resources) > 1:
        best = None
        for rx, ry in resources:
            if (rx, ry) == (tx, ty): 
                continue
            d = abs(rx - sx) + abs(ry - sy)
            # prefer resources that opponent is less likely to reach quickly
            slack = (abs(tx - ox) + abs(ty - oy)) - (abs(rx - ox) + abs(ry - oy))
            key = (-slack, d, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1] if best else (tx, ty)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # Deterministic preference order: toward target, then away from opponent, avoid obstacles, keep within bounds
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h: 
            continue
        if (nx, ny) in obstacles:
            continue
        d1 = abs(tx - nx) + abs(ty - ny)
        d_op = abs(ox - nx) + abs(oy - ny)
        # If stepping onto a resource cell, strongly prefer it
        on_res = 1 if (nx, ny) in set(tuple(p) for p in resources) else 0
        # Small bias to move generally forward (toward opponent corner) to avoid stalling late-game
        forward_bias = -(nx - sx) * (1 if ox > sx else -1 if ox < sx else 0) - (ny - sy) * (1 if oy > sy else -1 if oy < sy else 0)
        score = (-10 * on_res, d1, -d_op, forward_bias, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]