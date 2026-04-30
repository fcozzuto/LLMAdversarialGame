def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        dx = 0 if abs(sx - tx) < 0.5 else (1 if tx > sx else -1)
        dy = 0 if abs(sy - ty) < 0.5 else (1 if ty > sy else -1)
        return [int(dx), int(dy)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def target_score(mx, my, tx, ty):
        if (tx, ty) in obstacles:
            return -10**12
        myd = cheb(mx, my, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        rel = opd - myd  # positive => we are closer
        # Encourage central resources but don't overfit.
        dist_center = abs(tx - cx) + abs(ty - cy)
        # Strongly prefer stealing (relative closeness).
        steal = 3.0 * rel
        center = -0.03 * dist_center
        # If opponent is already adjacent, still choose if we can match/beat next.
        my_next = cheb(mx, my, tx, ty)
        opp_next = opd
        tempo = 0.15 * (my_next == 1) - 0.05 * (opp_next == 1)
        return steal + center + tempo - 0.03 * myd

    best = None
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = -10**18
        for tx, ty in resources:
            v = max(v, target_score(nx, ny, tx, ty))
        # If we can't get anywhere, at least avoid getting stuck near hazards.
        if v > bestv:
            bestv = v
            best = (dx, dy)

    if best is not None:
        return [best[0], best[1]]

    # Fallback: step toward center.
    dx = 0 if abs(sx - cx) < 0.5 else (1 if cx > sx else -1)
    dy = 0 if abs(sy - cy) < 0.5 else (1 if cy > sy else -1)
    return [int(dx), int(dy)]