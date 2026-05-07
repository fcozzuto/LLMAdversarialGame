def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for x, y in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        # Prefer stealing chances: high (od - sd), then sooner for us, then deterministic tie-break.
        key = (od - sd, -sd, -(x + y), x, y)
        if best is None or key > best_key:
            best = (x, y)
            best_key = key
    tx, ty = best

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_m = [0, 0]
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Move toward target; if we can't, keep position. Prefer moves that also reduce opponent relative threat.
        key = (-nd, (od - nd), -(nx + ny), dx, dy)
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = [dx, dy]
    return best_m