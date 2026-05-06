def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        ax -= bx
        ay -= by
        ax = -ax if ax < 0 else ax
        ay = -ay if ay < 0 else ay
        return ax if ax > ay else ay

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in sorted(legal):
            v = cheb(sx + dx, sy + dy, cx, cy)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    legal = sorted(legal)
    best_move = legal[0]
    best_score = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        min_self_t = None
        best_diff = None
        for rx, ry in resources:
            self_t = cheb(nx, ny, rx, ry)
            opp_t = cheb(ox, oy, rx, ry)
            diff = opp_t - self_t
            if min_self_t is None or self_t < min_self_t:
                min_self_t = self_t
            if best_diff is None or diff > best_diff:
                best_diff = diff

        # Prefer grabbing a resource where we can arrive earlier, then reduce our own arrival time.
        score = best_diff * 100 - (min_self_t if min_self_t is not None else 0)

        # If tied, prefer moves that reduce distance to the closest resource and then deterministic by (dx,dy).
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            self_t = cheb(nx, ny, resources[0][0], resources[0][1])
            cur_t = cheb(sx + best_move[0], sy + best_move[1], resources[0][0], resources[0][1])
            if self_t < cur_t or (self_t == cur_t and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]