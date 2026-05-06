def choose_move(observation):
    w = observation.get("grid_width", 0) or 0
    h = observation.get("grid_height", 0) or 0
    try:
        w, h = int(w), int(h)
    except:
        return [0, 0]
    if w <= 0 or h <= 0:
        return [0, 0]

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    # Choose best resource deterministically: nearest (Cheb), then lexicographic.
    if resources:
        best_res = min(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
    else:
        best_res = (ox, oy)

    # Counter diagonal-probing: prefer moves that reduce opponent distance to their likely diagonal approach,
    # while still improving own distance to the best resource.
    best_move = None
    best_score = -10**18

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        d_res_now = cheb(nx, ny, best_res[0], best_res[1])
        d_res_cur = cheb(sx, sy, best_res[0], best_res[1])
        res_gain = d_res_cur - d_res_now  # positive is good

        d_op_now = cheb(nx, ny, ox, oy)
        d_op_cur = cheb(sx, sy, ox, oy)
        opp_proximity_gain = d_op_cur - d_op_now  # positive means moving closer to opponent

        # "Deny" if this move also increases opponent's distance from the best resource.
        if resources:
            d_op_to_res_now = cheb(ox, oy, best_res[0], best_res[1])
            # opponent position unchanged; but our move can change whether we reach first:
            # approximate by how much our distance shrinks relative to theirs.
            deny = (d_op_to_res_now - d_res_now)
        else:
            deny = 0

        # Small tie-break bias: avoid stepping away from center a lot, to keep mobility.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_now = cheb(nx, ny, cx, cy)
        center_cur = cheb(sx, sy, cx, cy)
        center_gain = center_cur - center_now

        score = 3.0 * res_gain + 1.2 * deny + 0.6 * center_gain + 0.25 * opp_proximity_gain

        if best_move is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]