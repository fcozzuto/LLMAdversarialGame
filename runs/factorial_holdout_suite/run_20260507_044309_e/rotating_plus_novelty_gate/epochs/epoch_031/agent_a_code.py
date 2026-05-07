def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    # Immediate capture
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            for rx, ry in resources:
                if nx == rx and ny == ry:
                    return [dx, dy]

    valid = [(dx, dy, sx + dx, sy + dy) for dx, dy in dirs if inb(sx + dx, sy + dy)]
    if not valid:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_key = None

    # Evaluate each move by how well it secures a resource earlier than opponent.
    # Score for move: max margin over resources (opp_time - our_time). Tie-break toward closer-secured resource and center.
    for dx, dy, nx, ny in valid:
        if resources:
            best_margin = -10**9
            best_r = None
            for rx, ry in resources:
                our_t = cheb(nx, ny, rx, ry)
                opp_t = cheb(ox, oy, rx, ry)
                margin = opp_t - our_t
                if margin > best_margin:
                    best_margin = margin
                    best_r = (rx, ry, our_t, opp_t)
                elif margin == best_margin and best_r is not None:
                    # prefer resources we can reach sooner when margins tie
                    if our_t < best_r[2] or (our_t == best_r[2] and opp_t < best_r[3]):
                        best_r = (rx, ry, our_t, opp_t)
            rx, ry, our_t, opp_t = best_r
            dist_center = abs(nx - cx) + abs(ny - cy)
            # Strongly prioritize positive margin (secure); then minimal our_t; then center.
            key = (best_margin, -our_t, -opp_t, -dist_center)
        else:
            # No visible resources: just move toward center while minimizing distance to opponent
            dist_center = abs(nx - cx) + abs(ny - cy)
            dist_opp = cheb(nx, ny, ox, oy)
            key = (-dist_center, -dist_opp, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [best[0], best[1]]