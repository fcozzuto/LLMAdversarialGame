def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b, c, d): return max(abs(a - c), abs(b - d))
    if not resources:
        best = (999999, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if dx == 0 and dy == 0:
                    pass
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                d = cheb(nx, ny, ox, oy)
                if d < best[0]:
                    best = (d, dx, dy)
        return [best[1], best[2]]
    # Mode switch for material strategy change: even->self-farming, odd->contest opponent resources.
    contest = (observation.get("turn_index", 0) % 2 == 1)
    refx, refy = (ox, oy) if contest else (sx, sy)
    # Choose target resource with tie-break toward center-ish to reduce dithering.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_res = None
    best_key = None
    for rx, ry in resources:
        d = cheb(refx, refy, rx, ry)
        key = (d, abs(rx - cx) + abs(ry - cy))
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)
    tx, ty = best_res
    # Score candidate moves: improve distance to target, avoid obstacles, and occasionally block by moving closer to opponent.
    best_move = (None, -10**18)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            if dx == 0 and dy == 0:
                stay_pen = 0.25
            else:
                stay_pen = 0.0
            d_target = cheb(nx, ny, tx, ty)
            d_opp = cheb(nx, ny, ox, oy)
            # Block bonus: if opponent is near any resource, prioritize approaching those resources.
            opp_near_bonus = 0.0
            if contest:
                for rx, ry in resources:
                    if cheb(ox, oy, rx, ry) <= 1:
                        if cheb(nx, ny, rx, ry) <= cheb(ox, oy, rx, ry):
                            opp_near_bonus = 0.8
                            break
            # Obstacle proximity penalty (local).
            obs_pen = 0.0
            for odx in (-1, 0, 1):
                for ody in (-1, 0, 1):
                    ax, ay = nx + odx, ny + ody
                    if (ax, ay) in obstacles:
                        obs_pen -= 0.15
            # Prefer slightly reducing distance to opponent only in contest mode (materially different vs farming).
            opp_term = -0.15 * d_opp if contest else 0.02 * d_opp
            val = (-d_target) - stay_pen + opp_term + opp_near_bonus + obs_pen
            if val > best_move[1]:
                best_move = ([dx, dy], val)
    if best_move[0] is None:
        return [0, 0]
    return best_move[0]