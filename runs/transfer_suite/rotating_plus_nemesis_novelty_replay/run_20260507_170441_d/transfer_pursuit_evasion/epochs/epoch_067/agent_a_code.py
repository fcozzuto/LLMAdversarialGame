def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    evader = "evader" in (observation.get("self_role", "") or "").lower()

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    if resources:
        tx, ty = min(resources, key=lambda p: (man(sx, sy, p[0], p[1]), man(ox, oy, p[0], p[1]), p[0], p[1]))
    else:
        tx, ty = ox, oy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        ds = man(nx, ny, tx, ty)
        do = man(nx, ny, ox, oy)
        if evader:
            v = (-do, ds, nx, ny)
        else:
            v = (ds, -do, nx, ny)
        if bestv is None or v < bestv:
            bestv = v
            best = [dx, dy]
    if best is not None:
        return best

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            return [dx, dy]
    return [0, 0]