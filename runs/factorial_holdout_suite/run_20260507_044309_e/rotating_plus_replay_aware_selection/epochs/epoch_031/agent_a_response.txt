def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def step_options(x, y):
        opts = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    opts.append((0, 0))
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    opts.append((dx, dy))
        if (0, 0) not in opts:
            opts.append((0, 0))
        return opts

    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive => we reach earlier
            center = cheb(rx, ry, w // 2, h // 2)
            v = lead * 1000 - ds * 8 - center
            if best is None or v > best[0]:
                best = (v, rx, ry)
        _, tx, ty = best

        opts = step_options(sx, sy)
        best_move = None
        best_score = -10**18
        for dx, dy in opts:
            nx, ny = sx + dx, sy + dy
            ds2 = cheb(nx, ny, tx, ty)
            # prefer moves that keep lead vs opponent on the target, and collect sooner
            do2 = cheb(ox, oy, tx, ty)
            score = (do2 - ds2) * 1000 - ds2 * 10
            # small repulsion from obstacles by penalizing proximity (deterministic)
            if obstacles:
                md = 10**9
                for ax, ay in obstacles:
                    d = cheb(nx, ny, ax, ay)
                    if d < md: md = d
                score -= (4 - md) * 3 if md < 4 else 0
            if best_move is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    # If no visible resources, go toward center; avoid obstacles
    cx, cy = w // 2, h // 2
    opts = step_options(sx, sy)
    best_move = [0, 0]
    best_d = 10**18
    for dx, dy in opts:
        nx, ny = sx + dx, sy + dy
        d = cheb(nx, ny, cx, cy)
        if d < best_d:
            best_d = d
            best_move = [dx, dy]
    return best_move