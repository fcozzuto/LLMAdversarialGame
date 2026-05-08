def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    blocked = {(p[0], p[1]) for p in obstacles}
    resources = observation.get("resources") or []

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(a, b, x, y):
        return abs(a - x) + abs(b - y)

    if not resources:
        best = None
        best_move = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            if best is None or d < best:
                best = d
                best_move = [dx, dy]
        return best_move

    best_val = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # Race heuristic: maximize how much closer we are than the opponent to the best available resource.
        # Tie-break: prefer moves that also reduce our absolute distance to that chosen resource.
        chosen_adv = None
        chosen_self_d = None
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - self_d
            if chosen_adv is None or adv > chosen_adv or (adv == chosen_adv and self_d < chosen_self_d):
                chosen_adv = adv
                chosen_self_d = self_d
        # Small additional preference: don't drift away from opponent too much unless it helps race.
        drift_penalty = 0.01 * man(nx, ny, ox, oy)
        val = chosen_adv - drift_penalty
        if best_val is None or val > best_val or (val == best_val and chosen_self_d < best_val):
            best_val = val
            best_move = [dx, dy]

    return best_move