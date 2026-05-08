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

    # If already stuck, just move legal.
    legal_me = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not legal_me:
        return [0, 0]

    best = None
    best_val = -10**18

    for mdx, mdy in legal_me:
        my_next = (sx + mdx, sy + mdy)

        # Opponent (pursuer) will try to minimize our distance (capture ends, but radius is 0).
        opp_legal = []
        for odx, ody in dirs:
            ax, ay = ox + odx, oy + ody
            if ok(ax, ay):
                opp_legal.append((odx, ody))
        if not opp_legal:
            opp_best_d2 = dist2((ox, oy), my_next)
            opp_best_corner = max(corners, key=lambda c: dist2(c, my_next))
            worst = opp_best_d2
        else:
            opp_best_d2 = 10**18
            for odx, ody in opp_legal:
                a = (ox + odx, oy + ody)
                d = dist2(a, my_next)
                if d < opp_best_d2:
                    opp_best_d2 = d

            # Tie-break: prefer moving toward the farthest corner from opponent.
            # (Helps against direct pursuit; still deterministic.)
            far_corner = max(corners, key=lambda c: dist2(c, my_next))
            opp_best_corner = far_corner

            worst = opp_best_d2

        # Strongly prefer larger post-minimax distance; small preference to corner.
        corner_bonus = 0
        if opp_best_corner:
            corner_bonus = dist2(opp_best_corner, my_next) // 9

        val = worst * 100 + corner_bonus
        if best is None or val > best_val:
            best_val = val
            best = (mdx, mdy)

    return [int(best[0]), int(best[1])]