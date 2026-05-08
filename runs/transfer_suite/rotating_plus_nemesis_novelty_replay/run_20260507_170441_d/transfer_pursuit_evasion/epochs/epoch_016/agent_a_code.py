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

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    my = (sx, sy)
    opp = (ox, oy)
    target_corner = max(corners, key=lambda c: dist2(my, c))

    best = None
    best_val = float("-inf")
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_next = (nx, ny)

        # Opponent picks response to keep distance large and head to the far corner.
        worst = float("-inf")
        for odx, ody in dirs:
            ax, ay = ox + odx, oy + ody
            if not ok(ax, ay):
                continue
            opp_next = (ax, ay)
            d = dist2(my_next, opp_next)
            corner_pull = -0.15 * dist2(opp_next, target_corner)
            opp_score = d + corner_pull
            if opp_score > worst:
                worst = opp_score

        # We want to minimize opponent's best score (thus maximize its negative).
        val = -worst
        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best