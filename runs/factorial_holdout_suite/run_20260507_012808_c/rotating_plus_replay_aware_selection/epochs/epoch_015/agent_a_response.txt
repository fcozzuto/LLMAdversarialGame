def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    # Target selection: maximize "secure-first" margin; if none, minimize own distance.
    best_res = None
    best_val = None
    if resources:
        for r in resources:
            rx, ry = r[0], r[1]
            ds = cheb((sx, sy), (rx, ry))
            do = cheb((ox, oy), (rx, ry))
            # Extra tie-break: prefer resources that are "less aligned" with opponent row/col sweeps.
            align = min(abs(ry - oy), abs(rx - ox))
            val = (do - ds, -align, -ds, rx, ry)
            if best_val is None or val > best_val:
                best_val = val
                best_res = (rx, ry)

    if best_res is None:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda c: cheb((sx, sy), c))
    else:
        tx, ty = best_res

    # Choose move that most improves progress toward target while avoiding stepping into "bad vicinity".
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        dself = cheb((nx, ny), (tx, ty))
        dop = cheb((ox, oy), (tx, ty))
        # Prefer moves that reduce our distance and slightly increase opponent distance to that same target.
        score = (-dself, -(dop - dself), -abs(ny - oy), -abs(nx - ox), dx == 0 and dy == 0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]