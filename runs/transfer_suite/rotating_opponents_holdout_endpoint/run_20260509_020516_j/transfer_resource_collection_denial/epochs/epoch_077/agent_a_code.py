def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 8, 8

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = max(abs(nx - cx), abs(ny - cy))
                key = (-d, -(dx == 0 and dy == 0), dx, dy)
                if best is None or key > best:
                    best = key
                    ans = [dx, dy]
        return ans

    def dist(ax, ay, bx, by):
        return abs(ax - bx) if abs(ax - bx) > abs(ay - by) else abs(ay - by)

    # Pick best target deterministically: maximize our advantage and closeness.
    best_key = None
    tx = ty = None
    for x, y in resources:
        sd = dist(sx, sy, x, y)
        od = dist(ox, oy, x, y)
        key = (od - sd, -sd, -((x + y) & 1), -dist(ox, oy, x, y))
        if best_key is None or key > best_key:
            best_key = key
            tx, ty = x, y

    # Step toward target; if blocked, choose alternative that minimizes distance to target.
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            nd = dist(nx, ny, tx, ty)
            key = (-nd, -(dx == 0 and dy == 0), dx, dy)
            if best_move is None or key > best_move:
                best_move = key
                ans = [dx, dy]
    return ans