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

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_key = None
        best = None
        for x, y in resources:
            ds = md(sx, sy, x, y)
            do = md(ox, oy, x, y)
            # maximize (opponent far - self far) i.e., prioritize resources we can reach earlier; tie-break by shorter ds and then by position
            key = (do - ds, -ds, -md(sx, sy, w - 1, h - 1), x, y)
            if best_key is None or key > best_key:
                best_key, best = key, (x, y)
        tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Choose a step that moves toward target while avoiding immediate obstacle collisions.
    def step_ok(dx, dy):
        nx, ny = sx + dx, sy + dy
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    candidates = []
    for dx, dy in moves:
        if not step_ok(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        # primary: reduce manhattan to target; secondary: also keep away from opponent target pressure
        d1 = md(nx, ny, tx, ty)
        d2 = md(nx, ny, ox, oy)
        candidates.append((-(d1), d2, dx, dy))
    candidates.sort()
    if candidates:
        return [int(candidates[0][2]), int(candidates[0][3])]

    return [0, 0]