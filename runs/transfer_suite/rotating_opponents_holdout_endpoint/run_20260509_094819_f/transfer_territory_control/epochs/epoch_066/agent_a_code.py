def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if p and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    unclaimed = observation.get("unclaimed_cells") or []
    cells = []
    for p in unclaimed:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                cells.append((x, y))

    st = observation.get("self_territory") or []
    self_terr = set()
    for p in st:
        if p and len(p) == 2:
            self_terr.add((int(p[0]), int(p[1])))

    op = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(op[0]), int(op[1])

    frontier = set()
    if self_terr:
        for (x, y) in self_terr:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    frontier.add((nx, ny))
        frontier_targets = [c for c in cells if c in frontier]
    else:
        frontier_targets = []

    targets = frontier_targets if frontier_targets else cells
    if not targets:
        return [0, 0]

    scored = []
    for x, y in targets:
        d = man(sx, sy, x, y)
        od = man(ox, oy, x, y)
        adj = 0
        if self_terr:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                if (x + dx, y + dy) in self_terr:
                    adj = 1
                    break
        # Prefer near our frontier; also mildly prefer far from opponent to reduce contest.
        score = d - (2.0 if adj else 0.0) + (0.25 * od)
        scored.append((score, x, y))
    scored.sort()
    tx, ty = scored[0][1], scored[0][2]

    best_move = [0, 0]
    best_val = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = man(nx, ny, tx, ty)
        # If staying is equally good, prefer non-staying deterministically.
        if dx == 0 and dy == 0:
            val += 0.01
        if val < best_val:
            best_val = val
            best_move = [dx, dy]
    if best_move == [0, 0]:
        # Ensure legal by possibly stepping toward target even if frontier blocked.
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        cand = [dx, dy]
        nx, ny = sx + cand[0], sy + cand[1]
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return cand
        return [0, 0]
    return best_move