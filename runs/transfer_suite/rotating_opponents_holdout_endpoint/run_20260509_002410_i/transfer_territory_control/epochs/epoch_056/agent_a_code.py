def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    rsrc = observation.get("resources") or []
    for p in rsrc:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_score = -10**18
    best_move = [0, 0]

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    target = (ox, oy)
    if resources:
        target = min(resources, key=lambda r: (dist2(sx, sy, r[0], r[1]), r[0], r[1]))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = -dist2(nx, ny, target[0], target[1])
        score += -0.05 * dist2(nx, ny, ox, oy)
        score += -0.01 * dist2(nx, ny, sx, sy)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move