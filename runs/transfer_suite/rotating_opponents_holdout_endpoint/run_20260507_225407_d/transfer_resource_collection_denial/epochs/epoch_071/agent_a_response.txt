def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_cells = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs_cells.add((x, y))
        except Exception:
            pass

    resources = []
    for p in observation.get("resources") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs_cells:
                resources.append((x, y))
        except Exception:
            pass

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs_cells:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def t(ax, ay, bx, by):
        # Diagonal moves allowed; use Chebyshev distance as time proxy.
        dx, dy = abs(ax - bx), abs(ay - by)
        return dx if dx > dy else dy

    # Opponent sweep_rows tendency: if target row matches opponent row, opponent likely contests faster.
    opp_row = oy
    opp_col = ox

    best = None
    # Primary: capture advantage under time-to-resource.
    # Secondary: avoid contested sweep lines (same row/near same col).
    # Tertiary: prefer resources further from opponent once advantage is similar.
    for rx, ry in resources:
        self_t = t(sx, sy, rx, ry)
        opp_t = t(ox, oy, rx, ry)
        adv = opp_t - self_t  # positive = we arrive first sooner
        contested = 0
        if ry == opp_row:
            contested += 6
        if rx == opp_col:
            contested += 3
        if abs(ry - opp_row) <= 1:
            contested += 2
        # Slight central bias to reduce corner trap.
        center = -abs(rx - (w - 1) / 2.0) - abs(ry - (h - 1) / 2.0)
        key = (adv - contested, self_t, -(abs(rx - sx) + abs(ry - sy)), center, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))

    if best is None:
        return [0, 0]

    tx, ty = best[1]
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    cand = (dx, dy)
    if cand in legal:
        return [dx, dy]

    # Deterministic fallback: choose legal move that most reduces Chebyshev distance to chosen target,
    # with a small preference to keep advancing in the same direction.
    best_step = None
    curd = t(sx, sy, tx, ty)
    for sdx, sdy in legal:
        nx, ny = sx + sdx, sy + sdy
        d2 = t(nx, ny, tx, ty)
        progress = (curd - d2)
        align = (1 if (sdx == dx and sdy == dy) else 0) + (1 if (sdx == dx) else 0) + (1 if (sdy == dy) else 0)
        key = (progress, align, -abs(nx - tx) - abs(ny - ty), nx, ny)
        if best_step is None or key > best_step:
            best_step = key, (sdx, sdy)
    return [best_step[1][0], best_step[1][1]]