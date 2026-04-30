def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def best_resource_from(pos):
        best = None
        for r in resources:
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            d = dist(pos, (rx, ry))
            key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry), d)
        return None if best is None else best[1], best[2]

    my_target = None
    my_d = 10**9
    opp_target = None
    opp_d = 10**9
    t = best_resource_from((sx, sy))
    if t[0] is not None:
        my_target, my_d = t
    t2 = best_resource_from((ox, oy))
    if t2[0] is not None:
        opp_target, opp_d = t2

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_key = None

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            key = (-dist((nx, ny), (ox, oy)), nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move if best_move is not None else [0, 0]

    # If opponent is closer to their nearest resource, try to deny by increasing distance to opponent.
    # Otherwise, greedily step toward our nearest resource.
    deny = (opp_d < my_d) if (opp_target is not None and my_target is not None) else False

    target = None if deny else my_target
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if deny and opp_target is not None:
            key = (-dist((nx, ny), (ox, oy)), dist((nx, ny), opp_target), nx, ny)
        else:
            if target is None:
                key = (0, nx, ny)
            else:
                key = (dist((nx, ny), target), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]