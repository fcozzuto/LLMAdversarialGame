def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in sorted(legal):
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, cx, cy)
            key = (-d, d, dx, dy)  # prefer moving toward center (smaller d)
            key = (d, cheb(nx, ny, ox, oy), dx, dy)
            if best is None or key < best:
                best = key
        return [best[2], best[3]]

    best_move = None
    best_key = None
    for dx, dy in sorted(legal):
        nx, ny = sx + dx, sy + dy

        # Find a resource where we "beat" the opponent (largest distance advantage).
        best_gap = None
        best_self_d = None
        best_opp_d = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            gap = od - sd  # positive means we are closer than opponent to that resource
            if best_gap is None or gap > best_gap or (gap == best_gap and sd < best_self_d):
                best_gap, best_self_d, best_opp_d = gap, sd, od

        # If we can beat some resource, prioritize that; otherwise, retreat slightly while reducing our distance to the closest resource.
        if best_gap is not None and best_gap > 0:
            score = best_gap * 20 - best_self_d * 2
        else:
            closest = None
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if closest is None or d < closest:
                    closest = d
            retreat = cheb(nx, ny, ox, oy)
            score = retreat * 0.5 - closest * 1.5

        # Small tie-breakers to stay deterministic and avoid clustering on immediate opponent.
        key = (-score, cheb(nx, ny, ox, oy), best_opp_d if best_opp_d is not None else 0, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]