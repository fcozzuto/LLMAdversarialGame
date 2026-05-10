def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_options():
        return [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if (sx + dx, sy + dy) in obstacles or not inb(sx + dx, sy + dy):
            for mx, my in step_options():
                nx, ny = sx + mx, sy + my
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    return [mx, my]
            return [0, 0]
        return [dx, dy]

    best_t = None
    best_adv = -10**9
    best_selfd = 10**9
    best_lex = None

    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        lex = (rx, ry)
        if (adv > best_adv or
            (adv == best_adv and (sd < best_selfd or (sd == best_selfd and (best_t is None or lex < best_lex))))):
            best_adv = adv
            best_selfd = sd
            best_t = (rx, ry)
            best_lex = lex

    tx, ty = best_t

    curd = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_score = (10**9, 10**9, 10**9)

    for mx, my in step_options():
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer progress; then avoid stepping behind if opponent is already closer.
        rel = cheb(ox, oy, tx, ty) - nd
        score = (nd, -rel, mx*0 + my)  # deterministic tie-break via mx,my order encoded later
        if nd < best_score[0] or (nd == best_score[0] and (-rel, mx, my) > (-best_score[1], best_move[0], best_move[1])):
            best_score = score
            best_move = (mx, my)

    if best_move == (0, 0) and curd > 0:
        # Try any valid move that reduces distance, else stay.
        for mx, my in step_options():
            nx, ny = sx + mx, sy + my
            if inb(nx, ny) and (nx, ny) not in obstacles:
                if cheb(nx, ny, tx, ty) < curd:
                    return [mx, my]
    return [best_move[0], best_move[1]]