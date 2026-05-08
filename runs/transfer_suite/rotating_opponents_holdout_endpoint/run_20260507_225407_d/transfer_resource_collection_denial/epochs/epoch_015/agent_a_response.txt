def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_val = -10**18
    best_move = [0, 0]

    # Deterministic tie-break: prefer closer resource and then earlier direction in dirs order.
    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= gw or ny < 0 or ny >= gh:
            continue
        if (nx, ny) in obstacles:
            continue

        cur_best = -10**18
        cur_sd = 10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Race advantage: larger (od - sd) is better; tie-break by smaller sd.
            v = (od - sd) * 100 - sd
            if v > cur_best or (v == cur_best and sd < cur_sd):
                cur_best = v
                cur_sd = sd

        if cur_best > best_val or (cur_best == best_val and cur_sd < cheb(best_move[0] + sx, best_move[1] + sy, sx, sy)):
            best_val = cur_best
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]