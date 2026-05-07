def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    threat = dist((sx, sy), (ox, oy)) <= 2

    if resources:
        target = min(resources, key=lambda t: dist((sx, sy), t))
        tx, ty = target
    else:
        tx, ty = ox, oy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if threat:
            score = dist((nx, ny), (ox, oy))  # move away
        else:
            score = -dist((nx, ny), (tx, ty))  # move toward
            # small tie-break: prefer not to stand still
            if dx == 0 and dy == 0:
                score -= 0.01
        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda x: x[0], reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]