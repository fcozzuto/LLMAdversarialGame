def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obs_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obs_list)
    res_list = observation.get("resources", []) or []
    resources = []
    for p in res_list:
        try:
            x, y = p
            resources.append((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cell_score(x, y):
        if resources:
            best = None
            for r in resources:
                d = dist((x, y), r)
                od = dist((ox, oy), r)
                key = (od - d, -d)  # prefer resources we reach earlier; break ties closer
                if best is None or key > best[0]:
                    best = (key, d, r)
            if best is None:
                return 0
            return best[0][0] * 10 + best[0][1]
        # No resources: move to increase distance from opponent deterministically
        return dist((x, y), (ox, oy)) * 2

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sc = cell_score(nx, ny)
        # Deterministic tie-break: prefer smaller dx, then smaller dy
        key = (sc, -abs(dx), -abs(dy), -dx, -dy)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]