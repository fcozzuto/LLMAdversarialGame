def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    resources = observation.get("resources", []) or []
    cand = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if (rx, ry) != (sx, sy) and (rx, ry) not in obs and inb(rx, ry):
                cand.append((rx, ry))

    if not cand:
        return [0, 0]

    # Guess opponent target: closest resource to opponent.
    ot = min(cand, key=lambda t: man(ox, oy, t[0], t[1]))
    oy_t = ot[1]

    best = None
    best_key = None
    for rx, ry in cand:
        d_self = man(sx, sy, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        key = (d_opp - d_self, -abs(ry - oy_t), -d_self)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = tx - sx
    dy = ty - sy
    step_options = []
    if abs(dx) >= abs(dy):
        step_options = [(1 if dx > 0 else -1 if dx < 0 else 0, 0), (0, 1 if dy > 0 else -1 if dy < 0 else 0)]
    else:
        step_options = [(0, 1 if dy > 0 else -1 if dy < 0 else 0), (1 if dx > 0 else -1 if dx < 0 else 0, 0)]

    for mx, my in step_options:
        nx, ny = sx + mx, sy + my
        if mx in (-1, 0, 1) and my in (-1, 0, 1) and inb(nx, ny) and (nx, ny) not in obs:
            return [mx, my]
    return [0, 0]