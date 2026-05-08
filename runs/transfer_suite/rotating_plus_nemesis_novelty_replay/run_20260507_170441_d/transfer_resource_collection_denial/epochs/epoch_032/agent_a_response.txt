def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None:
            obst.add((p[0], p[1]))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst
    if not resources:
        return [0, 0]

    best_dxdy = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate best resource to go for from this next cell.
        # Prefer: being closer than opponent, then being closer overall.
        # Also penalize staying still a bit.
        local_best = -10**18
        for rx, ry in resources:
            myd = max(abs(nx - rx), abs(ny - ry))
            opd = max(abs(ox - rx), abs(oy - ry))
            lead = opd - myd  # positive is good (I arrive first)
            # Strongly prefer leads, then shorter time; slight tie-break to keep moving.
            score = (lead * 10.0) - (myd * 1.2) - (max(0, myd - opd) * 3.0)
            if score > local_best:
                local_best = score

        local_best -= 0.05 * (dx == 0 and dy == 0)
        if local_best > best_score:
            best_score = local_best
            best_dxdy = (dx, dy)

    return [best_dxdy[0], best_dxdy[1]]