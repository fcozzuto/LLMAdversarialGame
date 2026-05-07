def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = -10**18
    best_move = [0, 0]

    my_pos = (sx, sy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        if not res:
            # retreat to center-ish while keeping away from opponent
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score = -abs(nx - cx) - abs(ny - cy) + 0.05 * md((nx, ny), (ox, oy))
        else:
            my_best = -10**18
            for rx, ry in res:
                my_d = md((nx, ny), (rx, ry))
                op_d = md((ox, oy), (rx, ry))
                if my_d == 0:
                    claim = 1e9
                else:
                    # Prefer resources we can reach no slower; otherwise minimize how much we trail.
                    ahead = op_d - my_d
                    claim = ahead * 100 - my_d * 2
                    if ahead < 0:
                        claim -= (-ahead) * 120
                # Slightly value nearer overall and penalize moving into opponent proximity.
                score_ = claim - my_d * 1 - 0.1 * md((nx, ny), (ox, oy))
                if score_ > my_best:
                    my_best = score_
            score = my_best

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move