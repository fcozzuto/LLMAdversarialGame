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
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in legal:
            v = cheb(sx + dx, sy + dy, cx, cy)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Deterministic tie-breaker order
    legal.sort()

    best = legal[0]
    best_score = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Evaluate each resource; prefer states where we're much closer than opponent.
        # Also bias toward nearest resource to avoid dithering.
        local_best = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # "Advantage" if we can beat opponent on this target quickly
            adv = d_op - d_me
            # capture bias: closer is better, especially when we already have some advantage
            closeness = -d_me
            # denial bias: if opponent is very close, prioritize shrinking our distance strongly
            deny = 0
            if d_op <= 2:
                deny = 3 * (2 - d_me)  # encourages pressing contested targets
            score = 6 * adv + 2 * closeness + deny
            if score > local_best:
                local_best = score
        # Small bonus for staying away from obstacles-adjacent "dead corners" via center pull
        cx, cy = (w - 1) // 2, (h - 1) // 2
        center_pull = -cheb(nx, ny, cx, cy) // 2
        local_best += center_pull

        if best_score is None or local_best > best_score:
            best_score = local_best
            best = (dx, dy)

    return [best[0], best[1]]