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

    self_evader = is_evader(observation.get("self_role"))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    my_to_corner = [min(dist2(sx, sy, cx, cy) for cx, cy in corners), 0]

    best_move = (0, 0)
    best_score = None

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not valid(nx, ny):
            nx, ny = sx, sy
        d = dist2(nx, ny, ox, oy)

        # Pursuer: minimize distance; Evader: maximize distance.
        if self_evader:
            corner_bonus = -min(dist2(nx, ny, cx, cy) for cx, cy in corners)
            score = (d, corner_bonus)
            better = best_score is None or score > best_score
        else:
            # Prefer moves that get closer and also reduce opponent's cornering options.
            opp_corner_dist = min(dist2(ox, oy, cx, cy) for cx, cy in corners)
            my_corner_dist = min(dist2(nx, ny, cx, cy) for cx, cy in corners)
            # If opponent is near a corner, try to approach that same corner.
            score = (-d, opp_corner_dist - my_corner_dist)
            better = best_score is None or score > best_score

        if better:
            best_score = score
            best_move = (ddx, ddy)

    return [int(best_move[0]), int(best_move[1])]