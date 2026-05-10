def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    def norm(p):
        try:
            x, y = p
            return int(x), int(y)
        except Exception:
            return None

    sp = norm(observation.get("self_position"))
    op = norm(observation.get("opponent_position"))
    if sp is None or op is None:
        return [0, 0]
    sx, sy = sp
    ox, oy = op

    obstacles = set()
    for o in observation.get("obstacles") or []:
        q = norm(o)
        if q is not None:
            obstacles.add(q)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    role = (observation.get("self_role") or "pursuer").lower()
    is_evader = role == "evader"

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # If evader: run away; if pursuer: chase. Handle wall-run by preferring moves
    # that increase accessible freedom (avoid dead-ends).
    best = None
    best_score = None

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    dx_dir = 0 if ox == sx else (1 if ox > sx else -1)
    dy_dir = 0 if oy == sy else (1 if oy > sy else -1)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = dist2((nx, ny), (ox, oy))
        fn = free_neighbors(nx, ny)

        # Wall-run mitigation:
        # - pursuer: prioritize reducing distance; break ties by moving toward opponent direction and into open space
        # - evader: prioritize increasing distance; break ties by moving opposite opponent direction and into open space
        align = (dx_dir * dx + dy_dir * dy)
        if is_evader:
            score = (-d, -fn, align)
        else:
            score = (d, -fn, -align)

        if best is None or score < best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]