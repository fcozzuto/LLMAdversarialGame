def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    for dx, dy, nx, ny in valid:
        if (nx, ny) in res_set:
            return [dx, dy]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    best_move = (0, 0)
    best_score = -10**18

    # Two-phase: prefer resources I can reach no later than opponent; if none, still move toward best "near-win" target.
    for dx, dy, nx, ny in valid:
        my_pos_adv = 0
        candidate_score = -10**18
        for rx, ry in resources:
            dme = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # urgency (smaller is better), advantage (positive if I arrive earlier/equal)
            adv = do - dme
            # slight bias toward intercepting opponent's progress line
            intercept = 2 if ry == oy else 0
            urgency = -dme
            score = 6 * adv + 1.5 * urgency + intercept
            # encourage securing if I can win/tie quickly
            if dme <= do:
                score += 12
                if dme == do:
                    score += 4
            my_pos_adv = max(my_pos_adv, adv)
            if score > candidate_score:
                candidate_score = score
        # if no resources, drift toward nearest corner opposite of opponent along horizontal first
        if not resources:
            candidate_score = -cheb(nx, ny, 0 if ox > w - 1 else w - 1, 0 if oy > h - 1 else h - 1)
        # deterministic tie-break: prefer staying if equally good, else smallest |dx|+|dy|
        total_step = abs(dx) + abs(dy)
        if candidate_score > best_score or (candidate_score == best_score and (total_step, dx, dy) < (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1])):
            best_score = candidate_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]