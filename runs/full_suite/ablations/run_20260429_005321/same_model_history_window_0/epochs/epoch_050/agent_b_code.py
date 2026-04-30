def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def nearest_from(px, py):
        if not resources:
            return (px, py)
        best = resources[0]
        bd = dist((px, py), best)
        for r in resources[1:]:
            d = dist((px, py), r)
            if d < bd:
                bd = d
                best = r
        return best

    my_t = nearest_from(sx, sy)
    op_t = nearest_from(ox, oy)

    tx, ty = my_t
    otx, oty = op_t

    # one-step greedy towards opponent target (for interception)
    def step_towards(px, py, qx, qy):
        dx = 0 if qx == px else (1 if qx > px else -1)
        dy = 0 if qy == py else (1 if qy > py else -1)
        nx, ny = px + dx, py + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            # try axis moves deterministically
            for sx2, sy2 in ((dx, 0), (0, dy), (0, 0), (-dx, -dy)):
                nx2, ny2 = px + sx2, py + sy2
                if inside(nx2, ny2) and (nx2, ny2) not in obstacles:
                    return (nx2, ny2)
        return (nx, ny)

    op_next = step_towards(ox, oy, otx, oty)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    res_set = set(tuple(r) for r in resources)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        # Main goal: reduce distance to our nearest resource
        d_now = dist((sx, sy), (tx, ty))
        d_after = dist((nx, ny), (tx, ty))
        score = (d_now - d_after) * 10

        # If we land on a resource, prioritize strongly
        if (nx, ny) in res_set:
            score += 500

        # Intercept opponent next greedy step
        if (nx, ny) == op_next:
            score += 250

        # Slightly prefer moves that keep us closer to opponent (to enable blocking), but only if not suicidal
        score += -0.2 * dist((nx, ny), (ox, oy))

        # Avoid giving up too much: prefer forward progress overall
        if (dx, dy) != (0, 0):
            score += 1

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]