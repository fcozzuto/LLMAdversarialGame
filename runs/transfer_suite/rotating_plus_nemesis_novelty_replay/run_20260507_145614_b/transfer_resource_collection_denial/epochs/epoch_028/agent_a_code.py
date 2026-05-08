def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    # Pick a contested-but-favorable target: prefer resources where we are closer than opponent,
    # otherwise prefer ones where we can still reduce the distance gap most.
    best_t = None
    best_key = (-10**18, 10**18)
    for rx, ry in resources:
        if not valid(rx, ry):
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        gap = od - sd  # positive means we are closer
        # tie-break: also prefer closer target overall
        key = (gap, -sd)
        if key > best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]

    rx, ry = best_t
    # Evaluate our next move: maximize progress toward target, while avoiding giving opponent too-good positions.
    best = (-10**18, -10**18, 10**18, 10**18)
    best_move = [0, 0]
    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue
        nd = man(nx, ny, rx, ry)
        sd = man(sx, sy, rx, ry)
        prog = sd - nd  # improvement toward target
        # Estimate how contested the target remains after we move
        my_gap = (man(ox, oy, rx, ry) - nd)  # higher is better for us
        # Also keep distance from opponent slightly to counter denial/blocking
        oppdist = man(nx, ny, ox, oy)
        # Prefer moves that keep oppdist from collapsing
        opp_score = oppdist
        key = (prog, my_gap, opp_score, -nd)
        if key > best:
            best = key
            best_move = [dxm, dym]

    return best_move