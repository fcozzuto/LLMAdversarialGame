def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources_raw = observation.get("resources", []) or []
    resources = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def blocked(x, y):
        return not (0 <= x < w and 0 <= y < h) or (x, y) in obstacles

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]
    if not resources:
        tx, ty = ox, oy
    else:
        best = None
        for x, y in resources:
            d = dist(sx, sy, x, y)
            if best is None or d < best[0] or (d == best[0] and (x < best[1] or (x == best[1] and y < best[2]))):
                best = (d, x, y)
        tx, ty = best[1], best[2]

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        candidates.append((dist(nx, ny, tx, ty), dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][1]), int(candidates[0][2])]