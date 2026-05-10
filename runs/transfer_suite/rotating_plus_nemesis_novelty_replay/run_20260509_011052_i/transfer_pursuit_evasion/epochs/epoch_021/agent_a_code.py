def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def corner_targets(x, y):
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        return min(corners, key=lambda c: abs(x - c[0]) + abs(y - c[1]))

    def king_dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def best_opponent_step(psx, psy):
        corner = corner_targets(ox, oy)
        best = None
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if not inside(nx, ny):
                continue
            # evader: prioritize staying closer to its nearest corner while maximizing distance from us
            corner_dist = abs(nx - corner[0]) + abs(ny - corner[1])
            dist_from_us = king_dist(nx, ny, psx, psy)
            val = -corner_dist + 2.2 * dist_from_us
            if val > best_val:
                best_val = val
                best = (nx, ny)
        return best if best is not None else (ox, oy)

    role = observation.get("self_role", "pursuer")
    if role == "evader":
        # Run from pursuer while staying oriented toward nearest corner (corner-camping)
        corner = corner_targets(sx, sy)
        best = (0, 0)
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            dist = king_dist(nx, ny, ox, oy)
            cd = abs(nx - corner[0]) + abs(ny - corner[1])
            val = 2.0 * dist - 0.8 * cd
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]]

    # pursuer: lookahead one step assuming opponent follows evasion_corner-like policy
    ox1, oy1 = best_opponent_step(sx, sy)
    best = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Prefer capture (distance 0) then minimize predicted post-move distance
        d_after = king_dist(nx, ny, ox1, oy1)
        score = -3.5 * d_after
        if d_after == 0:
            score += 1000.0
        # Also slightly improve wall-pressure on predicted position
        wall_prox = min(ox1, w - 1 - ox1, oy1, h - 1 - oy1)
        score -= 0.25 * wall_prox
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]