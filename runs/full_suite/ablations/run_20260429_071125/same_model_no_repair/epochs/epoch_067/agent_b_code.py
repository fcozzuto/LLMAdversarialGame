def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = [tuple(p) for p in (observation.get("resources") or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_val = -10**18

    if resources:
        for dx, dy, nx, ny in legal:
            v = 0
            # Race rule: maximize (opponent_dist - my_dist) to a resource after the move.
            local_best = -10**18
            my_d_op = cheb(nx, ny, ox, oy)
            for rx, ry in resources:
                if not inb(rx, ry) or (rx, ry) in obstacles:
                    continue
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                lead = do - ds  # positive means we are closer
                # If we can take the lead, strongly prefer; otherwise, minimize how badly we trail.
                if lead >= 0:
                    score = 12 * lead - 0.35 * ds - 0.15 * do
                else:
                    score = 3 * lead - 0.25 * ds - 0.05 * do
                # Mild preference to choose nearer resources overall (helps execution).
                score -= 0.02 * (ds + do)
                if score > local_best:
                    local_best = score
            # Extra pressure: don't drift toward opponent unless it helps lead to some resource.
            v = local_best - 0.03 * my_d_op - 0.01 * (abs(nx - cx) + abs(ny - cy))
            if v > best_val:
                best_val = v
                best_move = (dx, dy)
    else:
        # No resources: maximize distance from opponent while trending to center.
        for dx, dy, nx, ny in legal:
            v = 0.4 * cheb(nx, ny, ox, oy) - 0.02 * (abs(nx - cx) + abs(ny - cy))
            if v > best_val:
                best_val = v
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]