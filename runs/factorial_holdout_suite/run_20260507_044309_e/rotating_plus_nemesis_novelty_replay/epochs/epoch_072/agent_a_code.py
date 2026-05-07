def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Candidate next moves (stay included)
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Heuristic: maximize advantage for the best resource after moving.
    # Primary: (opp_dist - self_dist) to the best resource.
    # Secondary: smaller self_dist, tertiary: smaller cheb to center to reduce wandering.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    for dx, dy, nx, ny in moves:
        best_adv = -10**9
        best_selfd = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and sd < best_selfd):
                best_adv = adv
                best_selfd = sd
        center_pen = cheb(nx, ny, cx, cy)
        key = (best_adv, -best_selfd, -center_pen)
        if best is None or key > best[0]:
            best = (key, (dx, dy))

    return [best[1][0], best[1][1]]