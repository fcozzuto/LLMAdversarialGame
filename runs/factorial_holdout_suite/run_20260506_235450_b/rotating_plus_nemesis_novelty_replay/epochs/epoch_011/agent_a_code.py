def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def step_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        best = None
        for mx, my in cand:
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            key = (dist2(nx, ny, tx, ty), abs(nx - ox) + abs(ny - oy), nx, ny)
            if best is None or key < best:
                best = key
                best_move = [mx, my]
        return best_move if best is not None else [0, 0]

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda p: (dist2(sx, sy, p[0], p[1]), -dist2(ox, oy, p[0], p[1]), p[0], p[1]))
        return step_toward(tx, ty)

    best = None
    tx = ty = None
    for rx, ry in resources:
        self_d = dist2(sx, sy, rx, ry)
        opp_d = dist2(ox, oy, rx, ry)
        # Prefer resources where we have a "tempo" edge (opp further than us).
        # Also encourage earlier reach (self_d), and slight deterrence near opponent.
        key = (-(opp_d - self_d), self_d + 2 * (w * h - (abs(rx - ox) + abs(ry - oy))), rx, ry)
        if best is None or key < best:
            best = key
            tx, ty = rx, ry

    # If already on a resource cell, stay to secure; otherwise move deterministically toward chosen target.
    if (sx, sy) == (tx, ty):
        return [0, 0]
    return step_toward(tx, ty)