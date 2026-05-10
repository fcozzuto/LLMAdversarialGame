def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax + ay

    # Pick best resource: small self distance, large opponent distance, with light "blocking" bias
    best_i = 0
    best_key = None
    for i, (rx, ry) in enumerate(resources):
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        row_bonus = 1.0 if ry == oy else 0.0
        col_bonus = 0.5 if rx == ox else 0.0
        key = (sd - 1.2 * od - row_bonus - col_bonus, sd, -od, i)
        if best_key is None or key < best_key:
            best_key = key
            best_i = i

    tx, ty = resources[best_i]

    # Evaluate one-step moves toward target while keeping from walking into bad positions
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_score = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not in_bounds(nx, ny):
            continue
        # If move lands exactly on a resource, strongly prefer it.
        on_res = 0
        for (rx, ry) in resources:
            if rx == nx and ry == ny:
                on_res = 1
                break
        nd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        # Prefer closer to target; and if opponent is closer, try to increase their threat
        score = (-1000 * on_res) + nd - 0.8 * od
        # Small preference for moving onto same row/col as opponent to deny sweep opportunities
        if ny == oy:
            score -= 0.8
        if nx == ox:
            score -= 0.4
        # Mildly avoid getting farther from any resource cluster
        if score is not None and (best_score is None or score < best_score):
            best_score = score
            best_mv = (mx, my)

    dx, dy = best_mv
    return [int(dx), int(dy)]