def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obs.add((int(o[0]), int(o[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    best_score = float("-inf")
    best_move = [0, 0]
    my = (sx, sy)
    opp = (ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_next = (nx, ny)

        # Predict opponent response: maximize distance from our next position.
        opp_best = None
        opp_best_d = float("-inf")
        opp_best_corner = -1
        for odx, ody in dirs:
            ax, ay = ox + odx, oy + ody
            if not ok(ax, ay):
                continue
            a = (ax, ay)
            d = dist2(a, my_next)
            if d > opp_best_d:
                opp_best_d = d
                opp_best_corner = max(dist2(a, c) for c in corners)
                opp_best = a
            elif d == opp_best_d:
                csc = max(dist2(a, c) for c in corners)
                if csc > opp_best_corner:
                    opp_best_corner = csc
                    opp_best = a

        if opp_best is None:
            opp_best = opp

        after = dist2(opp_best, my_next)
        # Main objective: minimize post-response distance (maximize negative).
        score = -after
        # Small tiebreakers to prefer closing directly.
        score += 0.01 * (-dist2(opp, my_next))
        score += 0.001 * (-dist2(opp_best, my))
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move