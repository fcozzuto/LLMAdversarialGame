def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    selfT = toset(observation.get("self_territory"))

    targets = unclaimed or resources or set()
    if not targets:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1), (0, 0)]
    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def score_cell(x, y):
        sd = md(sx, sy, x, y)
        od = md(ox, oy, x, y)
        lock = 0
        if selfT and (x, y) not in selfT:
            for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x + ax, y + ay) in selfT:
                    lock = 3
                    break
        return (od - sd) + lock

    # Prefer stepping into a good neighbor target; otherwise move toward best cell.
    best_dir = (0, 0)
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        val = -md(nx, ny, ox, oy) * 0.01  # tiny tie-break bias
        if (nx, ny) in targets:
            val += 1000 + score_cell(nx, ny)
        # also consider adjacent targets reachable next
        for ax, ay in dirs[:4]:
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in targets:
                val += 50 + score_cell(tx, ty)
        if val > best_val:
            best_val = val
            best_dir = (dx, dy)

    if best_dir == (0, 0):
        # fallback: deterministic greedy toward best target
        best_t = None
        best_s = -10**9
        for (x, y) in targets:
            s = score_cell(x, y)
            if s > best_s or (s == best_s and (x, y) < best_t):
                best_s = s
                best_t = (x, y)
        tx, ty = best_t
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        for ddx, ddy in ((dx, 0), (0, dy), (dx, dy), (1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)):
            nx, ny = sx + ddx, sy + ddy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [ddx, ddy]
        return [0, 0]

    return [best_dir[0], best_dir[1]]