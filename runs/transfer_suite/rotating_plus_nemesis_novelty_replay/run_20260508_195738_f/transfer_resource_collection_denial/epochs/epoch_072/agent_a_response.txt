def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        # Head to corner farthest (cheb) from opponent, bias away from our current if possible.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (cheb(c[0], c[1], ox, oy), -cheb(c[0], c[1], sx, sy)))
        best = (10**9, 10**9)
        best_move = [0, 0]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if (d, cheb(nx, ny, ox, oy)) < best:
                best = (d, cheb(nx, ny, ox, oy))
                best_move = [dx, dy]
        return best_move

    best_score = (-10**18, 10**18, 10**18)  # (primary, self_dist, -advantage_closer)
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate best contested resource from this position.
        local_best_adv = -10**18
        local_best_selfd = 10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer to the same resource than opponent
            # Prefer securing resources we're closer to; if we can't, still move to reduce worst-case.
            if adv > local_best_adv or (adv == local_best_adv and sd < local_best_selfd):
                local_best_adv, local_best_selfd = adv, sd

        # Secondary: actual distance to that locally best resource (prefer nearer).
        # Tertiary: if equal, keep away from opponent (avoid stepping into their pursuit).
        opp_near = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        score = (local_best_adv, local_best_selfd, -opp_near)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move