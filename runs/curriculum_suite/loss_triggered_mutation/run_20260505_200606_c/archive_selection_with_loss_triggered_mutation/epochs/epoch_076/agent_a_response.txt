def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = man(nx, ny, ox, oy) - 0.05 * man(nx, ny, cx, cy)
            if bestv is None or v > bestv or (v == bestv and (nx, ny) < best):
                bestv = v
                best = (nx, ny)
        return [best[0] - sx, best[1] - sy] if best else [0, 0]

    best_move = (0, 0)
    best_score = None
    # Deterministic tie-break order: earlier in moves list
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Prefer a resource where we can be closer than opponent (opp_d - me_d),
        # then prefer smaller me_d, then prefer staying nearer to center.
        best_res = None
        best_key = None
        for rx, ry in resources:
            me_d = man(nx, ny, rx, ry)
            op_d = man(ox, oy, rx, ry)
            # Primary: how much closer we are than opponent (maximize opp_d - me_d)
            # Secondary: minimize our distance to that resource
            # Tertiary: minimize opponent distance (slight)
            # Tiebreak: deterministic by coordinates
            key = (-(op_d - me_d), me_d, op_d, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_res = (rx, ry)
        # Convert best_key to a scalar-ish score with deterministic comparisons
        # so movement with larger (op_d - me_d) wins; then nearer me_d; then center.
        rx, ry = best_res
        me_d = man(nx, ny, rx, ry)
        op_d = man(ox, oy, rx, ry)
        score_tuple = (-(op_d - me_d), me_d, man(nx, ny, cx, cy), nx, ny)
        if best_score is None or score_tuple < best_score:
            best_score = score_tuple
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]