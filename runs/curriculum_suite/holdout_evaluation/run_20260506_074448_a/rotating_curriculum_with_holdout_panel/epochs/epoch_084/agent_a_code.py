def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    resources = [(r[0], r[1]) for r in (observation.get("resources") or [])
                 if 0 <= r[0] < w and 0 <= r[1] < h and (r[0], r[1]) not in obstacles]
    if not resources:
        # move to center deterministically
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
                    if best is None or d < best[0]:
                        best = (d, dx, dy)
        return [0, 0] if best is None else [best[1], best[2]]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx if abs(dx) >= abs(dy) else dy * dy  # square of chosen axis distance

    def metric(rx, ry):
        myd = max(abs(rx - sx), abs(ry - sy))
        opd = max(abs(rx - ox), abs(ry - oy))
        # prefer being closer; discourage letting sweep-row opponent grab their current row resources
        row_pen = 4 if ry == oy else 0
        # small bias toward nearer resources to reduce late-game dithering
        return (myd - 0.95 * opd + row_pen, myd, opd)

    target = resources[0]
    bestm = metric(target[0], target[1])
    for rx, ry in resources[1:]:
        m = metric(rx, ry)
        if m < bestm:
            bestm = m
            target = (rx, ry)

    tx, ty = target
    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                before = max(abs(sx - tx), abs(sy - ty))
                after = max(abs(nx - tx), abs(ny - ty))
                # prefer reducing distance; tie-break toward resources closer than opponent
                d1 = after - before
                myd = after
                opd = max(abs(nx - ox), abs(ny - oy))
                tie = (myd - 0.95 * opd + (4 if ty == oy else 0), myd)
                score = (d1, tie)
                if best is None or score < best[0]:
                    best = (score, dx, dy)
    return [0, 0] if best is None else [best[1], best[2]]