def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    # If stuck on invalid (shouldn't happen), just stay.
    if sx < 0 or sy < 0 or sx >= w or sy >= h:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        # Chebyshev distance matches grid king-moves
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    my_pos = (sx, sy)
    opp_pos = (ox, oy)

    # Target selection: prefer resources where we are closer than opponent; otherwise nearest overall.
    best_res = None
    best_key = None
    if resources:
        for r in resources:
            rx, ry = r
            if (rx, ry) in obstacles:
                continue
            d_me = dist(my_pos, (rx, ry))
            d_op = dist(opp_pos, (rx, ry))
            # Key: heavily favor being closer; tie-break by smaller d_me and then by coordinates.
            key = (0 if d_me <= d_op else 1, d_me, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_res = (rx, ry)

    # If no resources, go toward center while staying away from opponent.
    if best_res is None:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        target = (int(round(tx)), int(round(ty)))
    else:
        target = best_res

    # Evaluate all legal deltas; avoid obstacles if possible.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_t = dist((nx, ny), target)
        d_o = dist((nx, ny), opp_pos)
        # Encourage nearing target and increasing distance from opponent; slight bias to reduce risk.
        # If we are behind on the chosen resource, we prioritize speed; otherwise we also try to separate from opponent.
        key_extra = 0
        if best_res is not None:
            d_me_now = dist(my_pos, best_res)
            d_op_now = dist(opp_pos, best_res)
            if d_me_now > d_op_now:
                key_extra = -0.2
            else:
                key_extra = 0.2
        score = (-d_t) + (0.05 * d_o) + key_extra
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    # If all moves blocked by obstacles (unlikely), stay.
    return [int(best_move[0]), int(best_move[1])]