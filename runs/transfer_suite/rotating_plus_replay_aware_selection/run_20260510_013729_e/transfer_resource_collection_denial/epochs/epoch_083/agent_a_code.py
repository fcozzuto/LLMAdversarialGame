def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obst
    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    # Choose best resource by winning likelihood: maximize (opp_dist - self_dist), then minimize self_dist
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd
        key = (adv, -sd)
        if best is None or key > best[0]:
            best = (key, (rx, ry), sd, od)
    _, (tx, ty), sd0, od0 = best
    chosen_adv = od0 - sd0

    # If we are not ahead, intercept: go to reduce opponent's distance to their closest resource.
    if chosen_adv <= 0:
        t2x, t2y = min(resources, key=lambda p: man(ox, oy, p[0], p[1]))
        tx, ty = t2x, t2y

    # Pick legal move that improves our primary objective deterministically
    best_move = (10**9, 10**9, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        selfd = man(nx, ny, tx, ty)
        if chosen_adv <= 0:
            oppd = man(ox, oy, tx, ty)
            oppd_next = man(ox, oy, tx, ty)  # opponent position unchanged this turn
            # primary: reduce our distance to opponent-target; secondary: keep close to other targets by reducing selfd overall
            score1 = selfd
            score2 = sd0  # constant-ish tie breaker to keep deterministic minimal change
            cand = (score1, score2, [dx, dy])
        else:
            # primary: minimize our distance to target; secondary: maximize advantage (opp_dist - self_dist) for that target
            oppd = man(ox, oy, tx, ty)
            adv_next = oppd - selfd
            cand = (selfd, -adv_next, [dx, dy])
        if cand[:2] < best_move[:2]:
            best_move = (cand[0], cand[1], cand[2])

    return best_move[2] if best_move[2] is not None else [0, 0]