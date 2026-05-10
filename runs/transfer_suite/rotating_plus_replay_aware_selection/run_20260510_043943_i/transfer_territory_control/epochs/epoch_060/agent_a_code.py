def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cand = []
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                cand.append((x, y))
                if len(cand) >= 30:
                    break

    if not cand:
        for p in observation.get("resources", []) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y):
                    cand.append((x, y))
                    if len(cand) >= 30:
                        break
    if not cand:
        cand = [(ox, oy)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(0, -1), (1, 0), (0, 0), (-1, 0), (0, 1)]
    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = 0
        for tx, ty in cand[:10]:
            ds = dist(nx, ny, tx, ty)
            do = dist(ox, oy, tx, ty)
            center = -0.02 * (abs(nx - w // 2) + abs(ny - h // 2))
            val += (do - ds) + center
        if val > best[0]:
            best = (val, dx, dy)

    if best[0] < -10**17 and inb(sx, sy):
        return [0, 0]
    return [best[1], best[2]]