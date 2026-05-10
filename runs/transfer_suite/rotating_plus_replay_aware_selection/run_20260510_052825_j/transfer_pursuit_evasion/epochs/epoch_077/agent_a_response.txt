def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    def open_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            if free(x + dx, y + dy):
                c += 1
        return c

    def opp_greedy_dist2(tx, ty):
        best = None
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not free(nx, ny):
                nx, ny = ox, oy
            d = dist2(nx, ny, tx, ty)
            if best is None or d < best:
                best = d
        return best if best is not None else dist2(ox, oy, tx, ty)

    best_val = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        dself = dist2(nx, ny, ox, oy)
        if evader:
            danger = opp_greedy_dist2(nx, ny)
            val = dself - 0.6 * danger
        else:
            val = -dself + 0.08 * open_neighbors(nx, ny)

        key = (val, -abs(dx) - abs(dy), dx, dy)  # deterministic tie-break
        if best_val is None or key > best_key:
            best_val = val
            best_key = key
            best_move = [dx, dy]

    return best_move