def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        # Target resource that we can contest: prefer (opp - self) large, then smaller self distance
        best = None
        for x, y in resources:
            d_self = dist2(sx, sy, x, y)
            d_opp = dist2(ox, oy, x, y)
            val = d_opp - d_self
            key = (val, -d_self)  # higher val, then smaller d_self
            if best is None or key > best[0]:
                best = (key, (x, y))
        tx, ty = best[1]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_self2 = dist2(nx, ny, tx, ty)
        d_opp2 = dist2(ox, oy, tx, ty)
        # Also consider immediate contest after our move: maximize advantage vs opponent in reaching target
        adv = d_opp2 - d_self2
        # Prefer getting the target sooner; tie-break deterministically by dx,dy ordering in list
        key = (adv, -d_self2, -dx * dx - dy * dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]