def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for o in obs_list:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Opponent likely evades: maximize distance from our new pos,
        # but also prefers moving toward its farthest corner.
        opp_best = -10**18
        for odx, ody in dirs:
            ax, ay = ox + odx, oy + ody
            if not ok(ax, ay):
                continue
            d = dist2(ax, ay, nx, ny)
            far_corner = max(dist2(ax, ay, cx, cy) for cx, cy in corners)
            score = d + 0.05 * far_corner
            if score > opp_best:
                opp_best = score
        # Our objective: after their response, minimize their distance from us.
        # Add a small term to reduce their access to corners (cut off escape).
        # (We use their best move distance as proxy.)
        # Compute our post-evade value by searching again for the maximizing response position.
        opp_best_d = -1
        opp_best_c = -1
        for odx, ody in dirs:
            ax, ay = ox + odx, oy + ody
            if not ok(ax, ay):
                continue
            d = dist2(ax, ay, nx, ny)
            far_corner = max(dist2(ax, ay, cx, cy) for cx, cy in corners)
            val = d + 0.05 * far_corner
            if abs(val - (opp_best)) <= 1e-9 or val == opp_best:
                if d > opp_best_d:
                    opp_best_d = d
                    opp_best_c = far_corner

        our_val = -opp_best_d - 0.01 * opp_best_c
        if best_val is None or our_val > best_val:
            best_val = our_val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best