def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if (sx, sy) in set(resources):
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def score_move(x, y):
        if not valid(x, y):
            return -10**9
        if resources:
            # Prefer moves that decrease distance to closest resource
            best = 10**9
            for rx, ry in resources:
                d = abs(x - rx)
                e = abs(y - ry)
                if e > d:
                    d = e
                if d < best:
                    best = d
            # Slightly prefer being farther from opponent
            po = abs(x - ox)
            pq = abs(y - oy)
            if pq > po:
                po = pq
            return 1000 - best + po * 0.01
        else:
            # No resources: move away from opponent
            po = abs(x - ox)
            pq = abs(y - oy)
            if pq > po:
                po = pq
            return po

    best_mv = None
    best_sc = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = score_move(nx, ny)
        if sc > best_sc or (sc == best_sc and best_mv is not None and (dx, dy) < best_mv) or (sc > best_sc and best_mv is None):
            best_sc = sc
            best_mv = (dx, dy)

    if best_mv is None:
        return [0, 0]
    return [int(best_mv[0]), int(best_mv[1])]