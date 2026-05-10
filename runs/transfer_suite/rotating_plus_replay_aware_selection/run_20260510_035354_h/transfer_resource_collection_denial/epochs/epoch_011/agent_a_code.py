def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_key = None
    best_t = None
    for rx, ry in resources:
        myd = kdist(sx, sy, rx, ry)
        opd = kdist(ox, oy, rx, ry)
        # Prefer winning races, then earlier arrival, then smaller lead, then closer to center, then top-left
        cx = rx - (w - 1) / 2.0
        cy = ry - (h - 1) / 2.0
        win = 1 if myd <= opd else 0
        lead = opd - myd
        key = (win, -myd, lead, -(cx * cx + cy * cy), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry, myd, opd)

    tx, ty, _, _ = best_t

    # Candidate moves: deterministic order (prefer diagonals aligned to target)
    dx_pref = 0 if tx == sx else (1 if tx > sx else -1)
    dy_pref = 0 if ty == sy else (1 if ty > sy else -1)
    candidates = [
        (dx_pref, dy_pref),
        (dx_pref, 0),
        (0, dy_pref),
        (dx_pref, -dy_pref),
        (-dx_pref, dy_pref),
        (-dx_pref, 0),
        (0, -dy_pref),
        (-dx_pref, -dy_pref),
        (0, 0),
    ]

    def cell_score(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obs:
            return (-10**9, 0)
        # Evaluate as next-step progress in race to chosen target, with slight row-sweep awareness
        myd = kdist(nx, ny, tx, ty)
        opd = kdist(ox, oy, tx, ty)
        win = 1 if myd <= opd else 0
        # tiny preference to move in direction of opponent's likely sweep (row pressure)
        row_bias = -(abs((ny - sy)) + 0.05 * abs(ox - nx))
        return (win, -myd + row_bias, -(abs(tx - nx) + abs(ty - ny)))

    best_move = (0, 0)
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        val = cell_score(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]