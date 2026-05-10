def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    capture_radius = observation.get("capture_radius", 0)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def king_dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def nearest_corner_dist(x, y):
        best = 10**9
        for cx, cy in corners:
            d = abs(x - cx) + abs(y - cy)
            if d < best:
                best = d
        return best

    def opponent_best_step(myx, myy, px, py):
        # Evader: maximize distance from us while staying closer to its nearest corner.
        best = None
        best_val = -10**18
        target_corner_dist = nearest_corner_dist(px, py)
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if not inside(nx, ny):
                continue
            corner_dist = nearest_corner_dist(nx, ny)
            dist_us = king_dist(nx, ny, myx, myy)
            # Small bias to keep running toward a corner (especially against wall-run patterns)
            # while maximizing separation.
            val = 2.4 * dist_us - 0.9 * corner_dist - 0.05 * target_corner_dist
            if val > best_val:
                best_val = val
                best = (nx, ny)
        return best if best is not None else (px, py)

    # If we can capture immediately, do it.
    if king_dist(sx, sy, ox, oy) <= capture_radius:
        return [0, 0]

    best_move = (0, 0)
    best_final = 10**18

    # Evaluate: our move + opponent best response, then minimize resulting distance to opponent.
    for dx0, dy0 in dirs:
        nsx, nsy = sx + dx0, sy + dy0
        if not inside(nsx, nsy):
            nsx, nsy = sx, sy  # engine would keep us; make it explicit
        nos = opponent_best_step(nsx, nsy, ox, oy)
        nox, noy = nos
        final_dist = king_dist(nsx, nsy, nox, noy)
        # Secondary term to avoid drifting away unnecessarily
        drift = nearest_corner_dist(nox, noy) - nearest_corner_dist(sx, sy)
        score = final_dist + 0.08 * drift
        if score < best_final:
            best_final = score
            best_move = (dx0, dy0)

    return [int(best_move[0]), int(best_move[1])]