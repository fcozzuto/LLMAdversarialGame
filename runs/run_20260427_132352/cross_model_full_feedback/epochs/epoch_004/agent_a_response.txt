def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    def best_target_from(px, py):
        if not resources:
            return None, None
        best_r = None
        best_adv = None
        best_dist = None
        for rx, ry in resources:
            sd = md(px, py, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd
            if best_adv is None or (adv, -sd, -(rx * 9 + ry)) > (best_adv, -best_dist, -(best_r[0] * 9 + best_r[1])):
                best_adv = adv
                best_dist = sd
                best_r = (rx, ry)
        return best_r, best_adv

    viable = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and not blocked(nx, ny):
            viable.append((dx, dy, nx, ny))
    if not viable:
        return [0, 0]

    center = (w // 2, h // 2)
    best_move = (0, 0, sx, sy)
    best_val = None
    for dx, dy, nx, ny in viable:
        r, adv = best_target_from(nx, ny)
        if r is None:
            target_score = -md(nx, ny, center[0], center[1])
            penalty = md(nx, ny, ox, oy) <= 1
            val = target_score - (10 if penalty else 0)
        else:
            sd = md(nx, ny, r[0], r[1])
            # Keep adv as primary, then reduce own distance; discourage getting too close to opponent.
            opp_close = md(nx, ny, ox, oy)
            val = (adv * 100) + (-sd) - (20 if opp_close <= 1 else 0) - (8 if opp_close <= 2 else 0)
            # Slight preference to keep relative pressure if already winning advantage.
            val += 3 if adv > 0 else 0
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = (dx, dy, nx, ny)

    return [best_move[0], best_move[1]]