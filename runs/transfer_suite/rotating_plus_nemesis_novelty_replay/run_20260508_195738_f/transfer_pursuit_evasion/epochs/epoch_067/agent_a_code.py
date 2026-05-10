def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    steps = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_step = (0, 0)
    best_val = -10**9

    nearest_res = None
    if resources:
        nearest_res = min(resources, key=lambda r: (manh(sx, sy, r[0], r[1]), r[0], r[1]))

    opp_dist = manh(sx, sy, ox, oy)
    avoid = opp_dist <= 2 and (nearest_res is None or manh(ox, oy, nearest_res[0], nearest_res[1]) < manh(sx, sy, nearest_res[0], nearest_res[1]))

    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if avoid:
            val = manh(nx, ny, ox, oy) * 100 - (manh(nx, ny, nearest_res[0], nearest_res[1]) if nearest_res else 0)
        else:
            if nearest_res:
                val = -manh(nx, ny, nearest_res[0], nearest_res[1]) * 100 - manh(nx, ny, ox, oy)
            else:
                cx, cy = (w - 1) // 2, (h - 1) // 2
                val = -manh(nx, ny, cx, cy) - manh(nx, ny, ox, oy)
        if val > best_val or (val == best_val and (dx, dy) < best_step):
            best_val = val
            best_step = (dx, dy)

    dx, dy = best_step
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]