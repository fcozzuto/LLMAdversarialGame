def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick target resource where we are likely to beat the opponent most deterministically
    best = resources[0]
    best_tv = None
    for r in resources:
        tx, ty = r[0], r[1]
        d_me = man(x, y, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        tv = (d_opp - d_me) * 1000 - d_me + (0.001 * d_opp)
        if best_tv is None or tv > best_tv or (tv == best_tv and (d_opp < man(x, y, best[0], best[1]))):
            best = r
            best_tv = tv
        elif tv == best_tv:
            if (tx, ty) < (best[0], best[1]):
                best = r
                best_tv = tv
    tx, ty = best[0], best[1]

    # Choose move that maximizes advantage after one step, avoiding obstacles if possible
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_ms = None
    cur_me = man(x, y, tx, ty)
    cur_opp = man(ox, oy, tx, ty)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        d_me = man(nx, ny, tx, ty)
        # Advantage: higher opp-self distance gap, then closer to target; slight preference for keeping us not behind
        ms = (cur_opp - d_me) * 1000 - d_me + 0.01 * cur_opp - 0.001 * d_me
        # Small tie-break: prefer moves that reduce manhattan to target
        if best_ms is None or ms > best_ms or (ms == best_ms and d_me < cur_me):
            best_ms = ms
            best_mv = (dx, dy)

    # If all candidate moves were blocked/out-of-bounds, stay (engine will keep us in place)
    if best_ms is None:
        return [0, 0]
    return [best_mv[0], best_mv[1]]