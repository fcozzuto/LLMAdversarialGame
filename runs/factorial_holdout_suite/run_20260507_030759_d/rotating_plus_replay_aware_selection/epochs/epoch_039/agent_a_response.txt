def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_score = -10**18
    best_tie1 = 10**18
    best_tie2 = -10**18
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        move_best_adv = -10**18
        move_best_sd = 10**18
        move_best_od = 10**18

        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive => we are closer
            if adv > move_best_adv or (adv == move_best_adv and (sd < move_best_sd or (sd == move_best_sd and od < move_best_od))):
                move_best_adv = adv
                move_best_sd = sd
                move_best_od = od

        # Prefer moves that maximize our best contest advantage.
        score = move_best_adv
        tie1 = move_best_sd      # then closer to that resource
        tie2 = -move_best_od     # then further from opponent's view (larger -od)
        if score > best_score or (score == best_score and (tie1 < best_tie1 or (tie1 == best_tie1 and tie2 > best_tie2))):
            best_score, best_tie1, best_tie2 = score, tie1, tie2
            best_move = [dx, dy]

    return best_move