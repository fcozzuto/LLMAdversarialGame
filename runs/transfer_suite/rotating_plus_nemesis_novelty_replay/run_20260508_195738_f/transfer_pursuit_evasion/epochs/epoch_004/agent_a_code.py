def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chase" in self_role) or ("tag" in self_role)
    if (("purs" not in self_role) and ("evad" not in self_role) and
        (("purs" in opp_role) or ("chase" in opp_role) or ("tag" in opp_role))):
        is_pursuer = False

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1,  0), (0,  0), (1,  0),
             (-1,  1), (0,  1), (1,  1)]

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    man2 = lambda ax, ay, bx, by: (ax - bx) * (ax - bx) + (ay - by) * (ay - by)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Evader: go to farthest corner; if already close, keep maximizing distance while staying mobile.
    # Pursuer: move greedily to reduce distance; if blocked, slide to best alternative.
    if is_pursuer:
        score_sign = 1  # lower is better: dist2 to opponent
        want = "min"
    else:
        score_sign = -1  # higher is better: dist2 from opponent
        want = "max"

    # Optional simple prediction of opponent direct step to avoid getting funneled.
    pred_x, pred_y = ox, oy
    dx_to = 0 if ox == sx else (1 if ox > sx else -1)
    dy_to = 0 if oy == sy else (1 if oy > sy else -1)
    if valid(ox + dx_to, oy + dy_to):
        pred_x, pred_y = ox + dx_to, oy + dy_to

    # Choose target for evader.
    if is_pursuer:
        tx, ty = ox, oy
    else:
        # Farthest corner from opponent (ties deterministic by corner list order)
        bestc = corners[0]
        bestd = man2(bestc[0], bestc[1], pred_x, pred_y)
        for c in corners[1:]:
            d = man2(c[0], c[1], pred_x, pred_y)
            if d > bestd:
                bestd, bestc = d, c
        tx, ty = bestc

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp2 = man2(nx, ny, pred_x, pred_y)
        d_tgt2 = man2(nx, ny, tx, ty)
        # Mobility: count valid neighbor moves from next cell.
        mob = 0
        for mdx, mdy in moves:
            nnx, nny = nx + mdx, ny + mdy
            if valid(nnx, nny):
                mob += 1

        if is_pursuer:
            # minimize distance to (predicted) opponent; break ties by mobility and then by target corner proximity
            val = d_opp2 * 1000 - mob * 10 + d_tgt2
            if best_val is None or val < best_val:
                best_val, best_move = val, (dx, dy)
        else:
            # maximize distance from predicted opponent; if equal, prefer heading toward target corner and higher mobility
            val = d_opp2 * 1000 + (10000 - d_tgt2) + mob * 10
            if best_val is None or val > best_val:
                best_val, best_move = val, (dx, dy)

    return [best_move[0], best_move[1]]