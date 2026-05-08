def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evasion" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def open_space(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    def block_cross(x, y, tx, ty):
        # If moving toward target would reduce reachable freedom, penalize.
        # (Simple, deterministic: count immediate obstacles around future cell)
        return 8 - open_space(x, y)

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        space = open_space(nx, ny)
        # tie-breakers: keep away/toward center depending on role
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)

        if is_evader:
            # maximize: distance to pursuer, freedom (avoid wall-running trap), mild center preference
            val = (d_opp * 4) + (space * 2) - int(center * 0.2) - block_cross(nx, ny, ox, oy)
        else:
            # minimize: distance to evader while keeping some freedom; avoid getting boxed in
            val = -(dist2(nx, ny, ox, oy) * 4) + (space * 2) - int(center * 0.05) - block_cross(nx, ny, ox, oy)

        if best_val is None or (val > best_val) or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]