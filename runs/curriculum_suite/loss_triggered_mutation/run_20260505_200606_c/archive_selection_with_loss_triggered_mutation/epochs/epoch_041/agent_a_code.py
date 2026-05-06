def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def best_resource_for_pos(px, py):
        if not resources:
            return None, 10**9, 10**9, 10**9
        best = None
        for rx, ry in resources:
            myd = md(px, py, rx, ry)
            opd = md(ox, oy, rx, ry)
            # If opponent sweep is strong, contest tends to happen on their approach paths.
            # Prefer targets on rows/columns less aligned with opponent to reduce direct contest.
            row_gap = abs(ry - oy)
            col_gap = abs(rx - ox)
            safe = 1 if myd <= opd else 0
            # Higher row/col gaps and safer contesting resources get priority.
            key = (safe, -(row_gap + col_gap), -(opd - myd), -myd)
            if best is None or key > best[0]:
                best = (key, (rx, ry), myd, opd)
        return best[1], best[2], best[3], best[0][3] if best else (None, 10**9, 10**9, 0)

    # If resources exist, pick move that maximizes immediate advantage on the best "safe" target.
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        target, myd, opd, _ = best_resource_for_pos(nx, ny)
        if target is None:
            continue
        # Extra bias: move that reduces distance to target and increases opponent distance.
        win = 1 if myd <= opd else 0
        # Avoid stepping into cells that block ourselves near obstacles (simple local penalty).
        obst_near = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                tx, ty = nx + adx, ny + ady
                if (tx, ty) in obstacles:
                    obst_near += 1
        # Small tie-breaker: prefer moves that change position (avoid dithering).
        moved = 0 if (dx == 0 and dy == 0) else 1
        key = (win, (opd - myd), -myd, (abs(target[0] - nx) + abs(target[1] - ny)), moved, -obst_near)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    if resources:
        return [best_move[0], best_move[1]]

    # No visible resources: drift away from center competition, but deterministically.
    # Prefer a move that increases Manhattan distance from opponent slightly.
    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        key = (md(nx, ny, ox, oy), -md(nx, ny, w // 2, h // 2), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]