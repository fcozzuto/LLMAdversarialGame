def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for p in obstacles:
        blocked.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    # Deterministic: prefer landing on a resource, else maximize (op_d - my_d) margin.
    # Also penalize moves that increase distance to the best "contested" resource.
    my_best_list = []
    for rx, ry in resources:
        myd = md(sx, sy, rx, ry)
        opd = md(ox, oy, rx, ry)
        my_best_list.append((rx, ry, myd, opd))

    # Choose a single target resource based on current margins: maximize opd-myd, but ensure we're not far behind.
    best_target = None
    best_key = None
    for rx, ry, myd, opd in my_best_list:
        margin = opd - myd
        key = (margin, -myd, -opd)  # higher margin, closer to it, and farther opponent
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target if best_target is not None else (sx, sy)

    best_score = None
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        # Immediate pickup
        on_resource = 1 if (nx, ny) in {(r[0], r[1]) for r in resources} else 0
        if on_resource:
            best_score = 10**9
            best_move = (dx, dy)
            break

        # Margin-based score over all resources: prefer being relatively closer than opponent.
        total = 0
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            margin = opd - myd
            # Contested resources matter more; unreachable via obstacles isn't modeled, so mild shaping only.
            wgt = 1
            if rx == tx and ry == ty:
                wgt = 3
            total += wgt * margin
        # Extra guidance: move toward chosen target, but don't sacrifice margin too much.
        d_to_target = md(nx, ny, tx, ty)
        d_to_opp = md(nx, ny, ox, oy)
        score = total * 10 - d_to_target - 0.05 * d_to_opp

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]