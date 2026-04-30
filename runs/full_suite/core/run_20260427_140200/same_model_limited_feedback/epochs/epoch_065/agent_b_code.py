def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    if not resources:
        return [0, 0]

    obs_set = set((x, y) for x, y in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_target = None
    best_score = -10**9
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = (do - ds) * 2 - ds * 0.2 + (0 if (rx, ry) == (sx, sy) else 0)
        if score > best_score:
            best_score = score
            best_target = (rx, ry)

    tx, ty = best_target if best_target is not None else resources[0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_obj = -10**18
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        dist_t = cheb(nx, ny, tx, ty)
        dist_o = cheb(nx, ny, ox, oy)
        obj = -dist_t * 3 + dist_o * 0.15
        if (nx, ny) == (tx, ty):
            obj += 1000
        if obj > best_obj:
            best_obj = obj
            best_move = [dx, dy]
        elif obj == best_obj:
            if (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]