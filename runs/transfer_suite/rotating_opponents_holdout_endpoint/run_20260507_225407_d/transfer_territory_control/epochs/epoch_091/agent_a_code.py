def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_terr.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.add((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    nbr4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    frontier = set()
    if self_terr and unclaimed:
        for c in unclaimed:
            x, y = c
            for dx, dy in nbr4:
                if (x + dx, y + dy) in self_terr:
                    frontier.add(c)
                    break

    candidates = sorted(frontier) if frontier else sorted(unclaimed)
    if candidates:
        tx, ty = candidates[0]
        bestd = man((sx, sy), (tx, ty))
        for c in candidates[1:]:
            d = man((sx, sy), c)
            if d < bestd or (d == bestd and c < (tx, ty)):
                tx, ty, bestd = c[0], c[1], d
        target = (tx, ty)
    else:
        target = (sx, sy)

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dtarget = man((nx, ny), target)
        dopp = man((nx, ny), (ox, oy))
        val = dtarget * 10 - dopp
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    if not (-1 <= best_move[0] <= 1 and -1 <= best_move[1] <= 1):
        return [0, 0]
    return best_move