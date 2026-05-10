def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or role.endswith("e")

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    def dist_manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    pred_corner = min(corners, key=lambda c: dist_manh(ox, oy, c[0], c[1]))
    icx, icy = pred_corner

    # Intercept point: stay one step "ahead" of predicted corner along the line from opponent to that corner.
    step_x = 0 if ox == icx else (1 if icx > ox else -1)
    step_y = 0 if oy == icy else (1 if icy > oy else -1)
    ix, iy = ox + step_x, oy + step_y
    if not (0 <= ix < w and 0 <= iy < h) or (ix, iy) in blocked:
        ix, iy = icx, icy

    def score(nx, ny):
        d_to_op = dist_manh(nx, ny, ox, oy)
        d_to_int = dist_manh(nx, ny, ix, iy)
        cheb = max(abs(nx - ox), abs(ny - oy))
        # pursuer: minimize; evader: maximize
        base = 10 * d_to_op + 3 * d_to_int + cheb
        return base if is_evader else -base

    # Deterministic tie-break: prefer moves that improve d_to_op (or worsen if evader), then lexicographic dx,dy.
    def key(move):
        dx, dy, nx, ny = move
        d = dist_manh(nx, ny, ox, oy)
        # fewer obstacles already handled; add small penalty for staying still to keep intent crisp
        stay_pen = 0 if (dx != 0 or dy != 0) else 1
        return (score(nx, ny), -d if not is_evader else d, -max(abs(nx - ox), abs(ny - oy)), -stay_pen, dx, dy)

    best = max(candidates, key=key) if not is_evader else max(candidates, key=key)
    # For evader, higher score desired; score() already returns base. For pursuer, score() returns negative base, but key uses max consistently.
    # Thus: pursuer should maximize key, evader also maximize key.
    return [int(best[0]), int(best[1])]