def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    x, y = self_pos
    ox, oy = opp_pos
    obs_set = set((p[0], p[1]) for p in obstacles)
    cand = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(nx, ny):
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1
        return nx, ny

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    # If no resources, drift toward opponent's side (likely better for scoring).
    if not resources:
        tx = w - 1 if ox < w / 2 else 0
        ty = h - 1 if oy < h / 2 else 0
        best = None
        bestd = 10**9
        for dx, dy in cand:
            nx, ny = clamp(x + dx, y + dy)
            if (nx, ny) in obs_set:
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    # Contested-resource heuristic: favor resources where we are closer than opponent.
    best_score = -10**18
    best_res = None
    for rx, ry in resources:
        sd = cheb(x, y, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Higher score is better:
        # - Prioritize we-beat-opponent (sd < od) strongly.
        # - Break ties using closeness and then fixed coordinate order.
        score = (od - sd) * 1000 - sd
        if best_res is None or score > best_score or (score == best_score and (rx, ry) < (best_res[0], best_res[1])):
            best_score = score
            best_res = (rx, ry)

    rx, ry = best_res
    # Move that reduces distance to chosen resource; if multiple, prefer moves that also increase distance from opponent.
    curd = cheb(x, y, rx, ry)
    best = None
    best_tuple = None
    for dx, dy in cand:
        nx, ny = clamp(x + dx, y + dy)
        if (nx, ny) in obs_set:
            continue
        nd = cheb(nx, ny, rx, ry)
        # Prefer improvement; if worse or equal, only pick if opponent gets no closer to us/target.
        oppd = cheb(ox, oy, rx, ry)
        new_oppd = cheb(ox, oy, rx, ry)  # opponent position unchanged this step
        opp_to_self = cheb(ox, oy, nx, ny)
        tup = (-(nd - curd), -nd, opp_to_self, (nx, ny))
        if best_tuple is None or tup > best_tuple:
            best_tuple = tup
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]