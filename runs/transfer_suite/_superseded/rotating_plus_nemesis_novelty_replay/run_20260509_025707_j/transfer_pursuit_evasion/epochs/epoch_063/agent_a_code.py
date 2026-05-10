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

    self_is_evader = is_evader(observation.get("self_role"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    if self_is_evader:
        # Run from opponent: maximize distance, prefer moving away on the axis with larger separation.
        pref = (1, 1)
        if abs(ox - sx) >= abs(oy - sy):
            pref = (1 if ox < sx else -1, 0)
        else:
            pref = (0, 1 if oy < sy else -1)
        best_move = None
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            away_bonus = 0
            if (ox < nx) == (sx < ox):  # discourage crossing direction incorrectly; acts as small stabilizer
                away_bonus -= 1
            if pref[0] != 0:
                away_bonus += 2 if dx * pref[0] > 0 else 0
            if pref[1] != 0:
                away_bonus += 2 if dy * pref[1] > 0 else 0
            # deterministic tie-break: higher distance, then higher away_bonus, then lexicographic (dx,dy)
            score = (d, away_bonus, -dx, -dy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move if best_move is not None else [0, 0]
    else:
        # Pursue opponent: minimize distance, prefer diagonal when it reduces both separations.
        best_move = None
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            reduce_both = 1 if (dx != 0 and dy != 0 and ((ox - nx) * (ox - sx) <= 0) and ((oy - ny) * (oy - sy) <= 0)) else 0
            towards_bonus = 0
            if dx != 0:
                towards_bonus += 1 if (ox > sx and dx == 1) or (ox < sx and dx == -1) else 0
            if dy != 0:
                towards_bonus += 1 if (oy > sy and dy == 1) or (oy < sy and dy == -1) else 0
            # deterministic tie-break: lower distance, then higher diagonal bonus, then higher towards_bonus, then lexicographic (dx,dy)
            score = (-d, reduce_both, towards_bonus, -dx, -dy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move if best_move is not None else [0, 0]