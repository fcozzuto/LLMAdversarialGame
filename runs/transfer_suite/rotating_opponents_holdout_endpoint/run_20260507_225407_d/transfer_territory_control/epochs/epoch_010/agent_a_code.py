def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass
    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        try:
            unclaimed.append((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if unclaimed:
        best = unclaimed[0]
        bestv = None
        for cx, cy in unclaimed:
            if (cx, cy) in obstacles:
                continue
            v = 2 * d((cx, cy), (ox, oy)) - d((cx, cy), (sx, sy))
            if bestv is None or v > bestv or (v == bestv and (cx, cy) < best):
                bestv = v
                best = (cx, cy)
        tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    far_opp = 0.0
    rc = observation.get("remaining_resource_count")
    if isinstance(rc, (int, float)):
        far_opp = 0.8 if rc <= 2 else 0.5
    for_obst = 0.0

    best_move = (0, 0)
    best_val = None
    for dx, dy, nx, ny in moves:
        val = far_opp * d((nx, ny), (ox, oy)) - d((nx, ny), (tx, ty)) - for_obst
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]