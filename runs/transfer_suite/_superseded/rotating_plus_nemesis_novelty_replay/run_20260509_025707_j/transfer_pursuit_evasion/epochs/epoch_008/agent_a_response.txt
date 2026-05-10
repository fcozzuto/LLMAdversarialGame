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

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    def free_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    role = (observation.get("self_role") or "pursuer").lower()
    is_evader = role == "evader"

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        f = free_count(nx, ny)
        # pursuer: minimize distance, prefer higher freedom
        # evader: maximize distance, prefer higher freedom
        if is_evader:
            score = (d, f, -(abs(nx - sx) + abs(ny - sy)))
        else:
            score = (-d, f, -(abs(nx - sx) + abs(ny - sy)))
        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: t[0], reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]