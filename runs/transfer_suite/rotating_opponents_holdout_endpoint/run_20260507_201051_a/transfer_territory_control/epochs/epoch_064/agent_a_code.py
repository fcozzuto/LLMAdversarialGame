def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles_raw = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    resources_raw = observation.get("resources") or []
    res = []
    for p in resources_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            if "position" in p and isinstance(p["position"], (list, tuple)) and len(p["position"]) >= 2:
                res.append((int(p["position"][0]), int(p["position"][1])))

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    target = (int(ox), int(oy))
    bestd = None
    for (rx, ry) in res:
        if not inside(rx, ry) or (rx, ry) in obstacles:
            continue
        d = manh(sx, sy, rx, ry)
        if bestd is None or d < bestd or (d == bestd and (rx, ry) < target):
            bestd = d
            target = (rx, ry)

    tx, ty = target
    dirs = [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0)]
    best = (-10**9, None)
    for dx, dy in dirs:
        nx, ny = int(sx + dx), int(sy + dy)
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d = manh(nx, ny, tx, ty)
        score = -d
        score -= 2 * manh(nx, ny, int(ox), int(oy))  # slightly discourage moving toward opponent
        key = (score, -d, -nx, -ny)
        if key > best[0] if isinstance(best[0], tuple) else (score > best[0][0] if isinstance(best[0], tuple) else score > best[0]):
            best = (score, (dx, dy))

    if best[1] is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]