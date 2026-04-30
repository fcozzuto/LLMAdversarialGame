def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            candidates.append((dx, dy))

    if not candidates:
        return [0, 0]

    resources_set = set(resources)
    if resources:
        rx0, ry0 = resources[0]
        ax, ay = (w // 2, h // 2)
    else:
        ax, ay = (w // 2, h // 2)

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_score = -10**18
    candidates.sort()
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        d_opp = dist(nx, ny, ox, oy)
        if resources:
            d_res = min(dist(nx, ny, rx, ry) for rx, ry in resources)
            score = -d_res + 0.2 * d_opp + (5 if (nx, ny) in resources_set else 0)
        else:
            score = -(dist(nx, ny, ax, ay)) + 0.2 * d_opp
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]