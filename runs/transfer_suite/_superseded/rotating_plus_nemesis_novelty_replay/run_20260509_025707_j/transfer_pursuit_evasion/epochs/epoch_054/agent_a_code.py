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

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def opp_best_move(myx, myy):
        # Opponent moves greedily relative to hypothetical our position.
        best = None
        best_d = None
        best_score = None
        for ddx, ddy in dirs:
            nx, ny = ox + ddx, oy + ddy
            if not valid(nx, ny):
                continue
            d = man(nx, ny, myx, myy)
            diag = 1 if (ddx != 0 and ddy != 0) else 0
            # If opponent is evader, they want larger distance; else smaller.
            score = d if opp_evade else -d
            if best is None:
                best = [ddx, ddy]
                best_d = d
                best_score = (score, diag)
            else:
                cand = (score, diag)
                if cand > best_score:
                    best = [ddx, ddy]
                    best_d = d
                    best_score = cand
        if best is None:
            return [0, 0]
        return best

    best_move = [0, 0]
    best_final = None
    best_tieb = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        opp_move = opp_best_move(nx, ny)
        ex, ey = ox + opp_move[0], oy + opp_move[1]
        if not valid(ex, ey):
            ex, ey = ox, oy
        d2 = man(nx, ny, ex, ey)
        # If we evade, keep distance; if pursue, reduce distance.
        diag = 1 if (dx != 0 and dy != 0) else 0
        # Capture occurs if after opponent move they coincide; approximate by our next position vs their next.
        # Since capture radius is 0, favor immediate capture when pursuer.
        capture_bonus = 10_000 if (nx == ex and ny == ey and not self_evade) else 0
        score = (d2 if self_evade else -d2) + capture_bonus
        tieb = (score, diag, -abs(dx), -abs(dy), dx, dy)
        if best_final is None or tieb > best_tieb:
            best_final = d2
            best_tieb = tieb
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]