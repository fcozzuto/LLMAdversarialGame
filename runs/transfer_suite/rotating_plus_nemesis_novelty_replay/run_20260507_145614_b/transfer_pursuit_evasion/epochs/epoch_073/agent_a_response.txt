def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    desired_dx = 0 if ox == sx else (1 if ox > sx else -1)
    desired_dy = 0 if oy == sy else (1 if oy > sy else -1)

    best = None
    best_key = None
    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        d_opp2 = dist2(nx, ny, ox, oy)
        man = abs(nx - ox) + abs(ny - oy)

        alignx = 1 if dxm == desired_dx else 0
        aligny = 1 if dym == desired_dy else 0
        diag_align = 1 if (dxm == desired_dx and dym == desired_dy and desired_dx != 0 and desired_dy != 0) else 0

        # Obstacle proximity penalty (prefer moving with "space" in front)
        min_obst = 10**9
        for bx, by in obst:
            dd = dist2(nx, ny, bx, by)
            if dd < min_obst:
                min_obst = dd
                if min_obst == 0:
                    break

        # Lower is better overall key
        key = (
            d_opp2,
            -diag_align,
            man,
            -(alignx + aligny),
            -(min_obst if min_obst != 10**9 else 0),
            dxm * 10 + dym
        )

        if best_key is None or key < best_key:
            best_key = key
            best = [dxm, dym]

    if best is None:
        return [0, 0]
    return best