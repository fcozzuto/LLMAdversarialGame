def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    t = observation.get("turn_index", 0)
    rem = observation.get("remaining_resource_count", len(resources))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    res = [(x, y) for (x, y) in resources if inb(x, y) and (x, y) not in obstacles]
    if not res:
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = -cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Strategy switch every other turn: race (prefer smallest own dist) vs denial (prefer largest opp dist - own dist).
    race_mode = (t & 1) == 0
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy, nx, ny in legal:
        # Mobility: avoid getting stuck near obstacles
        mob = 0
        for ax, ay in deltas:
            px, py = nx + ax, ny + ay
            if inb(px, py) and (px, py) not in obstacles:
                mob += 1

        # Evaluate the best resource after this move
        local_best = -10**18
        for rx, ry in res:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if race_mode:
                # Race: choose resources we are closer to, but also discourage giving opponent too good a shot
                v = (-d_self) + 0.6 * (d_opp - d_self)
            else:
                # Denial: maximize how much further the resource is from opponent relative to us
                v = (d_opp - d_self) - 0.25 * d_self
            # If resource is currently on our square, boost strongly
            if nx == rx and ny == ry:
                v += 50 + 0.5 * rem
            # Slightly prefer center-ish routes to reduce dead-ends
            cx, cy = (w - 1) // 2, (h - 1) // 2
            v += 0.02 * (-cheb(nx, ny, cx, cy))
            if v > local_best:
                local_best = v

        # Combine: prefer moves that improve local_best; if racing, also mildly prefer moving away from opponent early
        away = -cheb(nx, ny, ox, oy)
        val = local_best + (0.15 * away if race_mode else 0.05 * mob) + (0.02 * mob)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]