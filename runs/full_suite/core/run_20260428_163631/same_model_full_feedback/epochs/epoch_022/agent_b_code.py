def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w, h, sx, sy, ox, oy = int(w), int(h), int(sx), int(sy), int(ox), int(oy)

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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    moves = [d for d in deltas if ok(sx + d[0], sy + d[1])]
    if not moves:
        return [0, 0]

    def mdist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    cx, cy = w // 2, h // 2
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        oppd = mdist(nx, ny, ox, oy)
        if resources:
            mind = min(mdist(nx, ny, rx, ry) for rx, ry in resources)
            # Maximize: closer to resources, farther from opponent, slight central preference
            val = (-(mind), oppd, -mdist(nx, ny, cx, cy))
        else:
            val = (oppd, -mdist(nx, ny, cx, cy), 0)
        if best is None or val > best[0]:
            best = (val, [dx, dy])

    return best[1]