def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    res_set = set(tuple(p) for p in resources)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a target resource: prefer ones I'm closer to than opponent (lower score)
    target = None
    best = None
    for r in resources:
        rx, ry = r
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        score = md - 0.9 * od
        if best is None or score < best:
            best = score
            target = (rx, ry)
    if target is None:
        target = (w // 2, h // 2)

    tx, ty = target
    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_obj = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        my_d = cheb(nx, ny, tx, ty)
        obj = my_d
        if (nx, ny) in res_set:
            obj -= 5
        # Avoid getting too close to opponent when not on a resource
        op_d = cheb(nx, ny, ox, oy)
        obj += max(0, 3 - op_d) * 0.4
        if best_obj is None or obj < best_obj:
            best_obj = obj
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]