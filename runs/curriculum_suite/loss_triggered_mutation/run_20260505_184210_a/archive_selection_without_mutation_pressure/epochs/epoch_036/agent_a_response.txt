def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    # If no resources, head toward board center deterministically
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in sorted(legal):
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, cx, cy)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Score candidate moves by: (opp advantage) + (resource closeness) + (anti-dither)
    # Encourage moves that make us significantly closer to a good resource than opponent.
    opp_to_self = man(sx, sy, ox, oy)

    best = None
    best_score = None
    for dx, dy in sorted(legal):
        nx, ny = sx + dx, sy + dy
        best_res = None
        best_res_score = None
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer resources where opponent is farther.
            # Large weight on advantage; smaller weight on being close yourself.
            adv = opp_d - self_d
            val = adv * 100 - self_d
            if best_res_score is None or val > best_res_score:
                best_res_score = val
                best_res = (rx, ry, self_d, opp_d, adv)
        rx, ry, self_d, opp_d, adv = best_res

        # If we're already very close to opponent, avoid getting "body-blocked" by drifting into them.
        # Deterministic penalty based on resulting proximity.
        near_opp_pen = 0
        if man(nx, ny, ox, oy) <= 2:
            near_opp_pen = 40

        # Mild preference to reduce distance to chosen resource to prevent oscillation.
        self_progress = -self_d

        total = best_res_score + self_progress - near_opp_pen

        # Deterministic tie-break: smaller self distance to target, then smaller cheb to center, then lexical move.
        if best_score is None:
            best = (dx, dy)
            best_score = (total, self_d, cheb(nx, ny, (w - 1) // 2, (h - 1) // 2), dx, dy)
        else:
            cand = (total, self_d, cheb(nx, ny, (w - 1) // 2, (h - 1) // 2), dx, dy)
            if cand > best_score:
                best_score = cand
                best = (dx, dy)

    return [best[0], best[1]]