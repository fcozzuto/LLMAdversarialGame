def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def corner_goal(px, py):
        # evader-like: prefer the corner farthest from our current position
        # but if already near a corner, keep pushing within that corner region.
        return max(corners, key=lambda c: dist(px, py, c[0], c[1]))

    # If we can capture immediately, do it.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny) and nx == ox and ny == oy:
            return [dx, dy]

    # 1-step minimax: opponent moves to maximize distance & corner escape;
    # we choose our move that minimizes their best outcome.
    best = (0, 0)
    best_val = 10**18
    goal_corner = corner_goal(ox, oy)
    gx, gy = goal_corner

    for dx, dy in dirs:
        nsx, nsy = sx + dx, sy + dy
        if not ok(nsx, nsy):
            continue

        opp_best = -10**18
        for odx, ody in dirs:
            nox, noy = ox + odx, oy + ody
            if not ok(nox, noy):
                continue
            d = dist(nsx, nsy, nox, noy)
            # encourage corner hovering/escape: maximize corner distance from its "current" chosen goal area
            cd = dist(nox, noy, gx, gy)
            # slight obstacle-aware bias: discourage moving into our immediate neighborhood (so evader avoids being corner-trapped)
            neigh = 1 if dist(nsx, nsy, nox, noy) <= 2 else 0
            val = d + 0.35 * cd - 0.05 * neigh
            if val > opp_best:
                opp_best = val

        # minimize the opponent's best outcome; tie-break deterministically toward moves reducing our distance to opponent
        our_after = dist(nsx, nsy, ox, oy)
        if opp_best < best_val or (opp_best == best_val and our_after < dist(sx + best[0], sy + best[1], ox, oy)):
            best_val = opp_best
            best = (dx, dy)

    return [int(best[0]), int(best[1])]