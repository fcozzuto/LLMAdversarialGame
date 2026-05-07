def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if not resources:
        return [0, 0]

    occ = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in occ:
            continue

        # Find the best resource we would target from this next cell.
        # Score is minimized lexicographically.
        local_best = None
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Primary: prefer resources where we are closer than opponent (negative my_d-opp_d).
            # Secondary: faster arrival; then move away from opponent in coordinates to reduce contest.
            row_gap = abs(ry - oy)
            col_gap = abs(rx - ox)
            val = (my_d - opp_d, my_d, row_gap + col_gap)
            if local_best is None or val < local_best:
                local_best = val

        if local_best is None:
            continue
        if best_val is None or local_best < best_val:
            best_val = local_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]