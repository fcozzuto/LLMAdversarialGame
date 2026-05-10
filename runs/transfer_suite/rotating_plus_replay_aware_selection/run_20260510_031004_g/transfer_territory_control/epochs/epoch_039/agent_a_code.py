def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def is_blocked(x, y):
        return (x, y) in obstacles or not inb(x, y)

    def get_pos(r):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return (int(r[0]), int(r[1]))
        if isinstance(r, dict):
            p = r.get("position", r.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
        return None

    res = observation.get("resources", [])
    resources = []
    for r in res:
        p = get_pos(r)
        if p is not None and not is_blocked(p[0], p[1]):
            resources.append(p)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if is_blocked(nx, ny):
            continue

        if resources:
            d = min(max(abs(nx - rx), abs(ny - ry)) for (rx, ry) in resources)
            dopp = max(abs(nx - ox), abs(ny - oy))
            score = (-d, dopp)
        else:
            dopp = max(abs(nx - ox), abs(ny - oy))
            score = (dopp, 0)

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return list(best if best is not None else (0, 0))