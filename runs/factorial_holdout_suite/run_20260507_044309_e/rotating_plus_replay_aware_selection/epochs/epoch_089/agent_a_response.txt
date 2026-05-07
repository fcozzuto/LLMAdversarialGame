def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Strongly prefer resources we can reach earlier, then earlier by us,
            # then delay opponent. Deterministic tie by coordinates.
            key = (ds - do, ds, -do, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        # Deterministic center drift with slight corner bias based on who is "ahead" in x.
        tx, ty = (w // 2, h // 2)
        if sx < ox:
            tx = min(w - 1, tx + 1)
        else:
            tx = max(0, tx - 1)
        if sy < oy:
            ty = min(h - 1, ty + 1)
        else:
            ty = max(0, ty - 1)

    # Choose best immediate move by evaluating next position.
    cur = (sx, sy)
    best_mv = (None, None, None)  # (score, ds, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Primary: move toward chosen target.
        ds = cheb(nx, ny, tx, ty)
        # Secondary: avoid letting opponent get closer to any visible resource.
        opp_best = 10**9
        for rx, ry in (resources or []):
            if (rx, ry) in obstacles:
                continue
            dso = cheb(ox, oy, rx, ry)
            if dso < opp_best:
                opp_best = dso
        # Tertiary: discourage being cornered by obstacles (prefer positions with more legal neighbors).
        neigh = 0
        for adx, ady in moves:
            axx, ayy = nx + adx, ny + ady
            if legal(axx, ayy):
                neigh += 1
        # Overall score: lower is better.
        # Encourage reducing our distance and increasing our advantage (opponent distance - ours).
        adv = cheb(ox, oy, tx, ty) - ds
        score = (ds, -adv, -neigh, dx, dy)
        if best_mv[0] is None or score < best_mv[0]:
            best_mv = (score, ds, dx, dy)

    # If all moves illegal (rare), stay.
    if best_mv[0] is None:
        return [0, 0]
    return [best_mv[2], best_mv[3]]