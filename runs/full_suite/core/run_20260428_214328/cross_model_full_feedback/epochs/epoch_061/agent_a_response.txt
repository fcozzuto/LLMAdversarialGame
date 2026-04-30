def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y): obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obst:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a target: prefer resources where we are closer than opponent; break ties by overall distance.
    target = None
    if resources:
        best = None
        best_key = None
        for r in resources:
            myd = cheb((sx, sy), r)
            opd = cheb((ox, oy), r)
            key = (opd - myd, -(myd + 0.15 * opd), -r[0], -r[1])
            if best_key is None or key > best_key:
                best_key = key
                best = r
        target = best

    if target is None:
        target = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)

    # Move selection: greedy toward target, with avoidance of obstacles and slight opponent-consideration.
    def neighbor_ok(nx, ny):
        if not inside(nx, ny): return False
        if (nx, ny) in obst: return False
        return True

    def near_obst(nx, ny):
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                if (nx + dx, ny + dy) in obst:
                    cnt += 1
        return cnt

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not neighbor_ok(nx, ny):
            # invalid move -> remain, but still evaluate as (0,0) only once deterministically
            nx, ny = sx, sy
            dx, dy = 0, 0
        myd = cheb((nx, ny), target)
        opd = cheb((ox, oy), target)
        # Prefer reducing my distance; if opponent is nearer, also try to reduce opponent advantage.
        val = (-myd) + 0.35 * (opd - myd) - 0.08 * near_obst(nx, ny)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]