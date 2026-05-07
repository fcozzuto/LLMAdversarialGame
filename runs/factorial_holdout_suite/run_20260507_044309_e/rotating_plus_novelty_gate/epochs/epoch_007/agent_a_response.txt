def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in observation.get("obstacles", []):
        obstacles.add((p[0], p[1]))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    best_key = None
    best_move = [0, 0]

    # Precompute opponent distances to resources (Manhattan).
    opp_d = {}
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        opp_d[(rx, ry)] = man(ox, oy, rx, ry)
    if not opp_d:
        return [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        # From next cell, pick resource maximizing our capture priority.
        chosen = None
        for rx, ry in opp_d.keys():
            sd = man(nx, ny, rx, ry)
            od = opp_d[(rx, ry)]
            # Priority: beat opponent (negative slack), then quicker, then closer to top-left.
            slack = od - sd
            if chosen is None:
                chosen = (slack, -sd, -((7 - ry) * w + (7 - rx)))
            else:
                cand = (slack, -sd, -((7 - ry) * w + (7 - rx)))
                if cand > chosen:
                    chosen = cand

        if chosen is None:
            continue

        # Prefer moves that improve slack most; deterministic tie breaks.
        key = (chosen[0], chosen[1], chosen[2], nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move