def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [None, None])
    sx, sy = int(sx), int(sy)
    ox = None if ox is None else int(ox)
    oy = None if oy is None else int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    best_key = None

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            nearest = min(resources, key=lambda r: manh((nx, ny), r))
            dist = manh((nx, ny), nearest)
            opp_pen = 0
            if ox is not None and oy is not None:
                dpo = manh((nx, ny), (ox, oy))
                opp_pen = -dpo
            key = (dist, opp_pen, dx, dy)
        else:
            if ox is None or oy is None:
                key = (0, 0, dx, dy)
            else:
                key = (-manh((nx, ny), (ox, oy)), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]