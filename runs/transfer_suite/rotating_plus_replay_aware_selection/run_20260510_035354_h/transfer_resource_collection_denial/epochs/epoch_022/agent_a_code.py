def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            px, py = int(p[0]), int(p[1])
            obs.add((px, py))

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    best_r = resources[0]
    best_gain = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        gain = opd - myd
        if best_gain is None or gain > best_gain:
            best_gain = gain
            best_r = (rx, ry)

    tx, ty = int(best_r[0]), int(best_r[1])

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_dir = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obs:
            continue
        myd2 = dist(nx, ny, tx, ty)
        opd = dist(ox, oy, tx, ty)
        val = (opd - myd2) * 1000 - myd2
        if best_val is None or val > best_val:
            best_val = val
            best_dir = [dx, dy]

    return best_dir if best_val is not None else [0, 0]