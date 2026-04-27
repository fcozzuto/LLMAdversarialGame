def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles", []) or []))
    if not resources:
        # Drift toward center deterministically
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def cheb(a, b, c, d):
        ax = a - c
        ay = b - d
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax if ax > ay else ay
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    best = None
    best_move = [0, 0]
    # Deterministic iteration order already defined in moves
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_pos_on = 0
        if (nx, ny) in resources:
            my_pos_on = 1
        best_cost_here = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Encourage immediate pickup, discourage races where opponent is closer
            cost = myd
            if my_pos_on and nx == rx and ny == ry:
                cost -= 1000
            if opd < myd:
                cost += 6  # prefer resources where I'm not behind
                # If I can arrive soon while opponent is close, weigh more
                if opd == myd - 1:
                    cost += 2
            # Slight preference for nearer resources overall
            cost += 0.01 * (myd + opd)
            # If opponent is already on this resource cell, avoid if possible
            if ox == rx and oy == ry:
                cost += 20
            if best_cost_here is None or cost < best_cost_here:
                best_cost_here = cost
        if best_cost_here is None:
            best_cost_here = cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
        if best is None or best_cost_here < best:
            best = best_cost_here
            best_move = [dx, dy]
    return best_move