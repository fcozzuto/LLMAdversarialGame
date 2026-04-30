def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    if not resources:
        # drift toward center if no resources
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        # Choose resource that maximizes relative closeness to us
        best = None
        best_val = -10**9
        for rx, ry in resources:
            ds = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(oy - ry)
            val = (do - ds) * 10 - (ds * 1)  # prefer being closer than opponent
            if val > best_val:
                best_val = val
                best = (rx, ry)
        tx, ty = best

        # If opponent is much closer to our target, contest closer to them
        # by moving toward the cell that minimizes our distance while also
        # not letting them get there too quickly.
        # (Implemented implicitly by target choice above plus pathing below.)

    deltas = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    best_step = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Distance to target
        dself = abs(tx - nx) + abs(ty - ny)
        # Try to avoid moving into cells closer to opponent than to us (soft)
        dop = abs(tx - ox) + abs(ty - oy)
        # Evaluate next move relative to opponent's current distance to target
        score = (-dself * 100) + ((dop - (abs(tx - ox) + abs(ty - oy))) * 0)  # keep deterministic
        # Additional anti-trap: prefer reducing distance while also not increasing
        # opponent's advantage against the same target (contest)
        score += (abs(tx - ox) + abs(ty - oy) - (abs(tx - nx) + abs(ty - ny))) * 20
        # Small bias toward staying consistent with diagonal moves
        if dx != 0 and dy != 0:
            score += 1
        if score > best_score:
            best_score = score
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]