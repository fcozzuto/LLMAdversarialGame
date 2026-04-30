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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        # Move toward center to reduce being trapped
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        if inb(sx+dx, sy) and (sx+dx, sy) not in obstacles: return [dx, 0]
        if inb(sx, sy+dy) and (sx, sy+dy) not in obstacles: return [0, dy]
        if inb(sx+dx, sy+dy) and (sx+dx, sy+dy) not in obstacles: return [dx, dy]
        return [0, 0]

    # Deterministic scoring: prefer move that increases our lead to a good resource
    # and keeps us away from obstacles' vicinity and opponent's closeness.
    best_move = None
    best_score = -10**18
    for dx, dy, nx, ny in legal:
        # obstacle proximity penalty (local, small)
        obs_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    obs_pen += 7
        opp_close = cheb(nx, ny, ox, oy)
        local_score = -opp_close * 6 - obs_pen

        # Evaluate best resource target for this move
        target_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ourd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Strongly prefer resources where we are closer than opponent
            lead = opd - ourd
            # Encourage moving toward resources; discourage giving opponent an immediate capture advantage
            s = lead * 120 - ourd * 3 - cheb(ox, oy, rx, ry) * 0.8
            # Tiny tie-break based on resource position relative to center
            cx, cy = (w - 1) // 2, (h - 1) // 2
            s += -0.01 * (cheb(rx, ry, cx, cy))
            if s > target_best:
                target_best = s
        local_score += target_best

        if local_score > best_score:
            best_score = local_score
            best_move = [dx, dy]
    if best_move is None:
        return [0, 0]
    return best_move