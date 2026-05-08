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

    def nearest_corner_dist2(p):
        return min(dist2(p, c) for c in corners)

    # If we can capture immediately, do it.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny) and nx == ox and ny == oy:
            return [int(dx), int(dy)]

    # One-step minimax: opponent chooses move that maximizes our distance after their move.
    # We choose our move that minimizes that outcome, with a small corner-trap bias.
    best_val = None
    best_move = [0, 0]
    ti = int(observation.get("turn_index", 0))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_next = (nx, ny)

        worst = float("-inf")
        for odx, ody in dirs:
            ax, ay = ox + odx, oy + ody
            if not ok(ax, ay):
                continue
            opp_next = (ax, ay)
            d = dist2(my_next, opp_next)
            # tiny bias to prefer corner pressure regardless of opponent action
            d = d + 0.01 * nearest_corner_dist2(opp_next)
            if d > worst:
                worst = d

        # tie-break deterministically using turn parity and move direction ordering
        # lower is better
        tie = (dx * 3 + dy * 5 + (ti & 1)) & 7
        val = (worst, tie)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [int(dx), int(dy)]

    return best_move