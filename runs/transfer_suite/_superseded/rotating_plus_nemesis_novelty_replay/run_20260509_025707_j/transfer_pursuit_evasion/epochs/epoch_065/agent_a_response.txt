def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("runner" in r) or ("evasion" in r) or ("evasive" in r)

    self_evade = is_evader(observation.get("self_role"))
    opp_evade = is_evader(observation.get("opponent_role"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def clamp_move(mx, my, ddx, ddy):
        nx, ny = mx + ddx, my + ddy
        return (nx, ny) if valid(nx, ny) else (mx, my)

    def opponent_next_from(myx, myy):
        best = None
        best_val = None
        for ddx, ddy in dirs:
            nx, ny = clamp_move(ox, oy, ddx, ddy)
            # Opponent reacts relative to our hypothesized position.
            v = dist2(nx, ny, myx, myy)
            score = v if opp_evade else -v  # evade maximize distance, pursue minimize
            key = (score, abs(ddx) + abs(ddy), ddx, ddy)
            if best is None or key > best_val:
                best_val = key
                best = (nx, ny)
        return best

    # If we are evader, try to maximize distance after predicting opponent response.
    # If we are pursuer, try to minimize distance after predicting opponent response.
    best_move = (0, 0)
    best_key = None
    for ddx, ddy in dirs:
        nx, ny = clamp_move(sx, sy, ddx, ddy)
        opp_nx, opp_ny = opponent_next_from(nx, ny)
        v = dist2(nx, ny, opp_nx, opp_ny)
        if self_evade:
            primary = v
        else:
            primary = -v
        tie = (abs(ddx) + abs(ddy), ddx, ddy)  # deterministic tie-breaker
        key = (primary, tie[0], tie[1], tie[2])
        if best_key is None or key > best_key:
            best_key = key
            best_move = (ddx, ddy)

    return [int(best_move[0]), int(best_move[1])]