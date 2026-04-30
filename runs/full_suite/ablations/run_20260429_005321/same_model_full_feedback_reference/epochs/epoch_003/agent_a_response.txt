def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = {tuple(p) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    us = (sx, sy)
    op = (ox, oy)

    res = [tuple(r) for r in resources]
    if res:
        # Target selection: first try contestable resources (opp not strictly closer).
        contest = []
        for r in res:
            ds = md(us, r)
            do = md(op, r)
            if do >= ds:
                contest.append((do - ds, ds, r))
        if contest:
            contest.sort(key=lambda t: (t[0], t[1], t[2][0], t[2][1]))
            target = contest[0][2]
        else:
            # Otherwise go for resources where we are closest advantage.
            res.sort(key=lambda r: (md(us, r), -md(op, r), r[0], r[1]))
            target = res[0]
    else:
        # No resources visible: pressure toward the opponent side/corner.
        target = (w - 1, h - 1) if (sx + sy) < (ox + oy) else (0, 0)

    best_score = -10**18
    best_move = (0, 0)

    # Simple heuristic: maximize (op_to_target - our_to_target), keep distance from opponent.
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            # Still-stay is always allowed; for blocked moves, evaluate staying instead.
            if (dx, dy) != (0, 0):
                nx, ny = sx, sy
            else:
                continue
        new = (nx, ny)
        our_d = md(new, target)
        opp_d = md(op, target)
        sep = md(new, op)
        center_pen = abs(nx - cx) + abs(ny - cy)
        score = (opp_d - our_d) * 2 + sep * 0.35 - center_pen * 0.03
        # Small tie-break to avoid oscillations: prefer moves that reduce our distance to target.
        score += (md(us, target) - our_d) * 0.001
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]