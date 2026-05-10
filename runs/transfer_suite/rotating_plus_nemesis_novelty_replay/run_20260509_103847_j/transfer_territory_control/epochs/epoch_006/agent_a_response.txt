def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    adj = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def has_self_neighbor(x, y):
        for dx, dy in adj:
            if (x + dx, y + dy) in selfT:
                return True
        return False

    # Target selection: prefer unclaimed near our frontier; else near opponent; else opponent territory.
    frontier = []
    for (x, y) in selfT:
        for dx, dy in adj:
            nx, ny = x + dx, y + dy
            if (nx, ny) in unT:
                frontier.append((nx, ny))
    if frontier:
        tx, ty = min(frontier, key=lambda p: (dist(p[0], p[1], ox, oy), dist(p[0], p[1], sx, sy)))
    else:
        candidates = list(unT)
        if candidates:
            tx, ty = min(candidates, key=lambda p: (dist(p[0], p[1], ox, oy), dist(p[0], p[1], sx, sy)))
        elif opT:
            tx, ty = min(opT, key=lambda p: dist(p[0], p[1], sx, sy))
        else:
            tx, ty = ox, oy

    best = (0, 0)
    best_score = -10**18
    cx, cy = w // 2, h // 2

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy

        score = 0
        if (nx, ny) in unT:
            score += 60
        elif (nx, ny) in opT:
            score += 45
        else:
            score -= 2

        if has_self_neighbor(nx, ny):
            score += 18
        if (nx, ny) in selfT:
            score += 6

        # Push toward chosen target and toward center slightly.
        score += -3 * dist(nx, ny, tx, ty)
        score += -1 * dist(nx, ny, cx, cy)

        # Avoid moving away from target strongly.
        score += 2 * (dist(sx, sy, tx, ty) - dist(nx, ny, tx, ty))

        # Deterministic tie-break: prefer larger score, then lexicographically smaller (dx,dy)
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]