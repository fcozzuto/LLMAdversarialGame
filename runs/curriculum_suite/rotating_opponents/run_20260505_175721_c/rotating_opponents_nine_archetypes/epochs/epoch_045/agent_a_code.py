def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
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

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_t = resources[0]
    best_val = None
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        val = (od - sd) * 1000 - sd
        if best_val is None or val > best_val or (val == best_val and (tx, ty) < best_t):
            best_val = val
            best_t = (tx, ty)
    tx, ty = best_t

    dx = 0
    dy = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    candidates = []
    for ax in (-1, 0, 1):
        for ay in (-1, 0, 1):
            if ax == 0 and ay == 0:
                continue
            nx, ny = sx + ax, sy + ay
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((ax, ay))
    candidates.append((0, 0))

    def step_score(ax, ay):
        nx, ny = sx + ax, sy + ay
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        return (od2 - sd2) * 1000 - sd2, sd2, (nx, ny)

    best_a = (0, 0)
    best_s = None
    for ax, ay in candidates:
        s = step_score(ax, ay)
        if best_s is None or s > best_s or (s == best_s and (ax, ay) < best_a):
            best_s = s
            best_a = (ax, ay)

    return [int(best_a[0]), int(best_a[1])]