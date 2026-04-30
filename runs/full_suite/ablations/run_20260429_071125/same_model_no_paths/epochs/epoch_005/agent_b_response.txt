def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not w or not h:
        return [0, 0]
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    # Pick a small deterministic subset of promising resources: nearest to us (then by coords).
    rs = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            d = cheb(sx, sy, rx, ry)
            rs.append((d, rx, ry))
    rs.sort(key=lambda t: (t[0], t[1], t[2]))
    rs = rs[:5]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue

        center_pen = 0.05 * cheb(nx, ny, cx, cy)
        # Strongly prefer states where we are closer than the opponent for at least one resource.
        best_adv = -10**18
        best_our_dist = 10**18
        for _, rx, ry in rs:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - our_d  # larger => we are closer than opponent
            if adv > best_adv or (adv == best_adv and our_d < best_our_dist):
                best_adv = adv
                best_our_dist = our_d

        # Add mild preference for getting nearer to the chosen resource and not drifting away.
        drift_pen = 0.02 * (best_our_dist - cheb(sx, sy, rs[0][1], rs[0][2])) if rs else 0
        # If we can't be closer (best_adv <= 0), still choose the move with maximal adv,
        # but slightly reward smaller our distance to the nearest resource.
        near_pen = 0.03 * best_our_dist
        val = best_adv - near_pen - center_pen - drift_pen

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]