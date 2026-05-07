def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)
    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obs.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs:
                resources.append((rx, ry))

    if not resources:
        tx, ty = (gw - 1) // 2, (gh - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    def md(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax + ay

    # Diagonal-allowed: use Chebyshev distance approximation for arrival time.
    def cd(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    best = None
    best_key = None
    for tx, ty in resources:
        sd = cd(sx, sy, tx, ty)
        od = cd(ox, oy, tx, ty)
        # maximize advantage; break ties by closer self, then closer opponent, then coordinate
        key = (od - sd, -sd, -od, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    # Evaluate local moves, avoid moving into obstacles.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break order
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        self_d = cd(nx, ny, tx, ty)
        opp_d = cd(ox, oy, tx, ty)
        # Prefer reducing distance to target and improving advantage; small preference to move closer in manhattan too.
        val = ((opp_d - self_d), (-self_d), (-md(nx, ny, tx, ty)))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]