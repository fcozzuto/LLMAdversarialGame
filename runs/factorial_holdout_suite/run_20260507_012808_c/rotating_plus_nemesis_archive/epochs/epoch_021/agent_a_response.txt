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

    def cell_value(nx, ny):
        best = None
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = my_d - opp_d  # negative is good
            # Secondary: earlier arrival; Tertiary: avoid letting opponent get too close
            tert = cheb(rx, ry, ox, oy) - cheb(rx, ry, nx, ny)
            val = (adv, my_d, -tert)
            if best is None or val < best:
                best = val
        return best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in occ:
            continue
        val = cell_value(nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]