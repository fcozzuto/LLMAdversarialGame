def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    if (sx, sy) in set((int(r[0]), int(r[1])) for r in resources if isinstance(r, (list, tuple)) and len(r) >= 2):
        return [0, 0]

    best_r = None
    best_val = -10**18
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can claim: lower our distance, higher separation from opponent
        can_claim = 1 if sd <= od else -1
        val = can_claim * 1000 - sd * 20 + (od - sd) * 10
        if val > best_val:
            best_val = val
            best_r = (rx, ry)

    if best_r is None:
        # Fallback: move toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_r

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0), (-dx, dy), (dx, -dy), (-dx, 0), (0, -dy)]
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if inb(nx, ny) and (nx, ny) not in obs:
            return [int(mx), int(my)]
    return [0, 0]