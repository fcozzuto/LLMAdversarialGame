def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    # Choose a target resource I can reach earlier than the opponent (my_dist - opp_dist is minimal).
    best = None
    best_key = None
    for rx, ry in resources:
        md = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        key = (md - od, md, -rx, -ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best

    # Pick the move (including diagonals/stay) that improves distance to target and avoids obstacles.
    deltas = [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
    best_move = [0, 0]
    best_eval = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < observation.get("grid_width", 8) and 0 <= ny < observation.get("grid_height", 8):
            if (nx, ny) in obstacles:
                continue
        else:
            continue
        dist = abs(rx - nx) + abs(ry - ny)
        # Mild bias to approach sooner and increase opposition separation.
        opp_sep = abs(ox - nx) + abs(oy - ny)
        eval_key = (dist, -opp_sep, abs(dx)+abs(dy))
        if best_eval is None or eval_key < best_eval:
            best_eval = eval_key
            best_move = [dx, dy]

    return best_move if best_eval is not None else [0, 0]