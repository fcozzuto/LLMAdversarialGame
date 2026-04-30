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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_set = set(resources)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if safe(nx, ny) and (nx, ny) in res_set:
            return [dx, dy]

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d_opp = cd(nx, ny, ox, oy)
        if resources:
            d_res = min(cd(nx, ny, rx, ry) for rx, ry in resources)
        else:
            d_res = 10**9
        # Prefer closer to resources; if resources absent, prefer staying away from opponent.
        sc = (-d_res * 3) + (d_opp) + (0 if dx == 0 and dy == 0 else -0.1)
        if best is None or sc > best[0]:
            best = (sc, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]