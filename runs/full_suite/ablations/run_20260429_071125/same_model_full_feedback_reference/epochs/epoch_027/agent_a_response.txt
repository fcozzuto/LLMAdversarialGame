def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles:
        return [0, 0]
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def min_dist_to_resources(x, y):
        best = 10**9
        for rx, ry in resources:
            d = man(x, y, rx, ry)
            if d < best:
                best = d
        return best

    cx, cy = (w - 1) // 2, (h - 1) // 2
    opp_min = min_dist_to_resources(ox, oy)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_key = (-10**18, 10**9, 10**9)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_min = min_dist_to_resources(nx, ny)
        advantage = opp_min - self_min  # higher is better
        center_bias = abs(nx - cx) + abs(ny - cy)
        key = (advantage, -self_min, -center_bias)
        if key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move