def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def king(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    resources = sorted(resources)
    best_t = resources[0]
    best_tuple = None
    for rx, ry in resources:
        myd = king((sx, sy), (rx, ry))
        opd = king((ox, oy), (rx, ry))
        # Primary: prefer targets closer than opponent; Secondary: smaller my distance; Tertiary: larger opponent distance
        t = (opd - myd, -myd, opd, -rx, -ry)
        if best_tuple is None or t > best_tuple:
            best_tuple = t
            best_t = (rx, ry)

    tx, ty = best_t
    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_m = (0, 0)
    best_v = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd = king((nx, ny), (tx, ty))
        opd = king((ox, oy), (tx, ty))
        # Maximize relative advantage; small penalty for being stuck near obstacles isn't possible without full pathfinding, so only local advantage
        v = (opd - myd, -myd, -dx, -dy)
        if best_v is None or v > best_v:
            best_v = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]