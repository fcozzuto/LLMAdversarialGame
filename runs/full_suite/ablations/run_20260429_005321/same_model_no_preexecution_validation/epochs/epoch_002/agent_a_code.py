def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # If no resources: reduce opponent mobility by moving to maximize our distance while not walking away too much.
    if not resources:
        best = (0, 0)
        best_key = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                ok = cheb(nx, ny, ox, oy)
                lk = cheb(nx, ny, sx, sy)
                key = (-ok, lk, nx, ny)
                if best_key is None or key < best_key:
                    best_key = key
                    best = (dx, dy)
        return [best[0], best[1]]

    # Pick a target that we can plausibly reach before the opponent (contest-first).
    best_t = None
    best_t_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Lower is better for key: prioritize winning race, then closer target; deterministic tie-break.
        key = (-(1 if ds < do else 0), ds - do, ds, rx, ry)
        if best_t_key is None or key < best_t_key:
            best_t_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    # Move: choose a legal delta that improves race to target and keeps opponent at bay.
    best = (0, 0)
    best_key = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            ds2 = cheb(nx, ny, tx, ty)
            ds1 = cheb(sx, sy, tx, ty)
            do2 = cheb(nx, ny, ox, oy)
            do1 = cheb(sx, sy, ox, oy)
            # Prefer: closer to target, and not letting opponent get significantly closer to us.
            # Deterministic key: lower is better.
            key = (
                0 if ds2 <= ds1 else 1,                    # prefer not worsening our target distance
                (ds2 - ds1),                             # then improve race
                -do2,                                      # then maximize distance from opponent
                -(do2 - do1),                              # then prefer expanding gap
                abs((nx - tx)) + abs((ny - ty)),          # small tie-break towards exact
                nx, ny
            )
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)

    return [best[0], best[1]]