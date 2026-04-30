def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))

    if resources:
        def dist(ax, ay, bx, by):
            return abs(ax - bx) + abs(ay - by)

        best_t = resources[0]
        best_s = -10**18
        for rx, ry in resources:
            dS = dist(sx, sy, rx, ry)
            dO = dist(ox, oy, rx, ry)
            s = (dO - dS) * 10 - dS
            if dS == 0:
                s += 10**9
            if s > best_s:
                best_s = s
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obst:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        d_opp = abs(nx - ox) + abs(ny - oy)
        val = -d + 0.3 * d_opp
        if resources and (nx, ny) in resources:
            val += 10**8
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]