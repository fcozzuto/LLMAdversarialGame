def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    unclaimed_set = set(unclaimed)

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = None
    if unclaimed:
        bestd = 10**9
        for c in unclaimed:
            if c in obstacles or not inb(c[0], c[1]):
                continue
            d = abs(c[0] - sx) + abs(c[1] - sy)
            if d < bestd:
                bestd = d
                target = c

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if target is not None:
            score = (10000 if (nx, ny) in unclaimed_set else 0) - man((nx, ny), target)
        else:
            score = man((nx, ny), (ox, oy))
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move