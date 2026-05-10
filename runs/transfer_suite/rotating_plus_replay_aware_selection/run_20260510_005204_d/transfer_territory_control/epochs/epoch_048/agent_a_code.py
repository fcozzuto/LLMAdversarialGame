def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    last = None
    sp = observation.get("self_path") or []
    if sp and isinstance(sp, list):
        q = sp[-1]
        if q and len(q) >= 2:
            last = (int(q[0]), int(q[1]))

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = 0
        if last is not None and (nx, ny) == last:
            score -= 5
        if resources:
            nr = min(dist2((nx, ny), r) for r in resources)
            cr = min(dist2((sx, sy), r) for r in resources)
            score += (cr - nr) * 2
            score += -nr // 3
        else:
            score += -dist2((nx, ny), (ox, oy)) // 3
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]