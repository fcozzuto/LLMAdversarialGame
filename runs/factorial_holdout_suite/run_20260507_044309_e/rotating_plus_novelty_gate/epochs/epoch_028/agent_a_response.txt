def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    res_set = {(rx, ry) for rx, ry in resources}
    for dx, dy, nx, ny in valid:
        if (nx, ny) in res_set:
            return [dx, dy]

    if not resources:
        # drift to nearest corner-ish to avoid wasting turns
        tx = w - 1 if sx < w - 1 else 0
        ty = h - 1 if sy < h - 1 else 0
        bestm = (10**9, 0, 0)
        for dx, dy, nx, ny in valid:
            m = manh(nx, ny, tx, ty)
            if m < bestm[0] or (m == bestm[0] and (dx, dy) < (bestm[1], bestm[2])):
                bestm = (m, dx, dy)
        return [bestm[1], bestm[2]]

    # Strategic change: maximize immediate advantage to resources; if opponent is closer, switch to denial by minimizing opponent gain.
    best_choice = None
    for dx, dy, nx, ny in valid:
        cur_min = 10**9
        cur_opp_min = 10**9
        best_adv = -10**9
        # For each resource, compute (opp_dist - my_dist) after this move.
        for rx, ry in resources:
            if not inb(rx, ry):
                continue
            myd = manh(nx, ny, rx, ry)
            opd = manh(ox, oy, rx, ry)
            adv = opd - myd
            if adv > best_adv:
                best_adv = adv
            if myd < cur_min:
                cur_min = myd
            if opd < cur_opp_min:
                cur_opp_min = opd
        # Score: prioritize positive advantage; then close on targets; then reduce opponent's nearest resource distance (denial).
        # Tie-break deterministically by move ordering.
        score = (best_adv * 1000) - (cur_min) - (cur_opp_min * 0.1)
        move_key = (-(best_adv >= 0), -best_adv, cur_min, cur_opp_min, dx, dy)
        if best_choice is None or move_key < best_choice[0] or (move_key == best_choice[0] and score > best_choice[1]):
            best_choice = (move_key, score, dx, dy)

    return [best_choice[2], best_choice[3]]