def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def king_dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    # Predict opponent toward a corner that maximizes distance from us, then take one-step lookahead.
    # This differs from pure "move to current opponent" by aiming at the likely next evasion pivot.
    best_corner = None
    best_corner_score = -10**18
    for cx, cy in corners:
        score = king_dist(ox, oy, cx, cy) - 1.5 * king_dist(cx, cy, sx, sy)
        if score > best_corner_score:
            best_corner_score = score
            best_corner = (cx, cy)
    cx, cy = best_corner

    # One-step predicted opponent move maximizing (corner closeness - distance from us).
    best_ox, best_oy = ox, oy
    best_pred_val = -10**18
    for dx, dy in dirs:
        nx, ny = ox + dx, oy + dy
        if not inside(nx, ny):
            continue
        corner_closeness = -(abs(nx - cx) + abs(ny - cy))
        dist_from_us = king_dist(nx, ny, sx, sy)
        val = corner_closeness + 2.0 * dist_from_us
        if val > best_pred_val:
            best_pred_val = val
            best_ox, best_oy = nx, ny

    tx, ty = best_ox, best_oy

    # Greedy: move to reduce king distance to predicted target, with tie-breaker to keep moving toward that corner.
    best_move = (0, 0)
    best_val = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = king_dist(nx, ny, tx, ty)
        toward_corner = abs(nx - cx) + abs(ny - cy)
        val = d * 10 + toward_corner * 0.01
        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]