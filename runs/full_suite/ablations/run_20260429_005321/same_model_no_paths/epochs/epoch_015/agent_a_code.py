def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    for rx, ry in resources:
        if sx == rx and sy == ry:
            return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    adj8 = deltas

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    def nearest_res_score(nx, ny):
        if not resources:
            return 0
        best = None
        for rx, ry in resources:
            v = dist(nx, ny, rx, ry)
            if best is None or v < best:
                best = v
        return -best  # larger is better

    def obstacle_penalty(nx, ny):
        p = 0
        for dx, dy in adj8:
            if (nx + dx, ny + dy) in obstacles:
                p += 1
        return -p

    best_move = (0, 0)
    best_val = -10**18

    # deterministic tie-breaker: fixed delta order; update only on strict improvement
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = 0
        val += 4.0 * nearest_res_score(nx, ny)
        val += 0.9 * obstacle_penalty(nx, ny)
        if not resources:
            val += -0.1 * dist(nx, ny, ox, oy)
        else:
            # stay away from opponent while progressing to resources
            val += 0.15 * (-dist(nx, ny, ox, oy))
        # slight preference for captures by moving onto a resource cell
        if (nx, ny) in set(tuple(r) for r in resources):
            val += 1000.0
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]