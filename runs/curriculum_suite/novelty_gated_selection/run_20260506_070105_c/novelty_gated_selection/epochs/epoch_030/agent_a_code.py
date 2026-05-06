def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", None) or []
    obstacles = observation.get("obstacles", None) or []

    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            if d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    best_move = (0, 0)
    best_val = -10**18

    # Predict opponent next step by their greedy move toward the nearest resource.
    opp_moves = []
    for dx, dy in dirs:
        nx, ny = ox + dx, oy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            opp_moves.append((dx, dy, nx, ny))
    if not opp_moves:
        opp_moves = [(0, 0, ox, oy)]
    nearest_r = min(resources, key=lambda r: man(ox, oy, r[0], r[1]))
    opp_target = (nearest_r[0], nearest_r[1])
    opp_best = None
    for dx, dy, nx, ny in opp_moves:
        key = man(nx, ny, opp_target[0], opp_target[1]), man(nx, ny, ox, oy), dx, dy
        if opp_best is None or key < opp_best[0]:
            opp_best = (key, dx, dy, nx, ny)
    _, _, _, nox, noy = opp_best

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Evaluate our best resource target advantage over the opponent (using predicted opponent pos).
        best_margin = -10**18
        best_opp_r_dist = 10**18
        for rx, ry in resources:
            my_t = man(nx, ny, rx, ry)
            opp_t = man(nox, noy, rx, ry)
            margin = opp_t - my_t  # positive is good: we arrive earlier
            if margin > best_margin:
                best_margin = margin
            # Also track how close the opponent will be to any resource after we move.
            d_opp_any = man(nox, noy, rx, ry)
            if d_opp_any < best_opp_r_dist:
                best_opp_r_dist = d_opp_any

        # If we can't secure any advantage, play defense: choose move that makes opponent's best approach harder,
        # while still progressing toward resources.
        my_nearest = min(m for m in [man(nx, ny, r[0], r[1]) for r in resources]) if resources else 0
        val = 1000 * best_margin - 2.0 * best_opp_r_dist - 0.15 * my_nearest

        # Tie-break deterministically: prefer moves that reduce distance to the opponent's predicted position.
        val2 = val - 0.01 * man(nx, ny, nox, noy)
        if val2 > best_val:
            best_val = val2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]