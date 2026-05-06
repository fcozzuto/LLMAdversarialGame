def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []

    obs = set()
    for o in obstacles_raw:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not res:
        # deterministic: move toward opponent's corner (roughly deny space)
        tx, ty = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            key = (man(nx, ny, tx, ty), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Resource-denial heuristic:
    # choose move that maximizes best "arrive-first advantage" to some resource,
    # tie-break by closeness and then deterministic move ordering.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        top_adv = -10**9
        top_dist = 10**9
        top_res = None
        for rx, ry in res:
            d_us = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            adv = d_op - d_us  # positive means we are closer (likely to grab first)
            # Encourage grabbing sooner; also discourage giving opponent too good timing.
            score_adv = adv
            if d_us < top_dist or (d_us == top_dist and score_adv > top_adv):
                top_adv = score_adv
                top_dist = d_us
                top_res = (rx, ry)
            elif score_adv > top_adv:
                top_adv = score_adv
                top_res = (rx, ry)

        # secondary: also consider steering away from opponent from the chosen target
        rx, ry = top_res
        opp_d_here = man(nx, ny, ox, oy)
        # prefer breaking ties by taking more immediate/advantageous grabs
        key = (-top_adv, top_dist, -opp_d_here, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [int(best[1]), int(best[2])]