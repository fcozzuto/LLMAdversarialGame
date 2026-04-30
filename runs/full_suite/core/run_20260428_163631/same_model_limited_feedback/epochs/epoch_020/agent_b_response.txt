def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_score = -10**18

    # Choose a "priority" resource: we want one where we are not worse, prefer far opponent and close ourselves.
    best_target = None
    best_target_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = (myd, -opd)
        if best_target_key is None or key < best_target_key:
            best_target_key = key
            best_target = (rx, ry)

    tx, ty = best_target if best_target is not None else (sx, sy)

    # Evaluate each legal move (avoid obstacles) with a mixture of resource pursuit and opponent denial.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)  # opponent distance to our target (stationary estimate)

        # Denial: if opponent can reach target sooner or equal, we try to move to increase our relative advantage.
        myd_to_opp = cheb(nx, ny, ox, oy)

        # Additional denial: avoid stepping onto/near resources that opponent is uniquely close to.
        risk = 0
        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if od < md:  # opponent closer to that resource than we would be after this move
                if md == 0:
                    risk += 50
                else:
                    risk += 1 + (md - od)

        # Higher score is better.
        score = (-myd) + (myd_to_opp * 0.02) + ((opd - myd) * 2.0) - (risk * 0.5)
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]