def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escap" in role) or ("run" in role) or ("runner" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x, y):
        ax = abs(x - ox)
        ay = abs(y - oy)
        return ax if ax > ay else ay

    target_corner = None
    if is_evader:
        target_corner = max(corners, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), c[0], c[1]))

    best_move = (0, 0)
    first = True
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_opp = cheb(nx, ny)
        d_corner = 0
        if is_evader:
            d_corner = abs(nx - target_corner[0]) + abs(ny - target_corner[1])
            primary = (d_opp, d_corner, nx, ny)
        else:
            primary = (-d_opp, -(abs(nx - ox) + abs(ny - oy)), nx, ny)

        if first:
            best_move = [dx, dy]
            best_primary = primary
            first = False
        else:
            if is_evader:
                if primary > best_primary:
                    best_primary = primary
                    best_move = [dx, dy]
            else:
                if primary > best_primary:
                    best_primary = primary
                    best_move = [dx, dy]

    return best_move