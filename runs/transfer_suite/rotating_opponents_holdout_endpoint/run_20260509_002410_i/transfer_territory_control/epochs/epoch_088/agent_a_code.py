def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    resources = observation.get("resources") or []

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx, dy = ax - bx, ay - by
        return (dx * dx + dy * dy)

    opp_adj = set()
    for (x, y) in opp_t:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if 0 <= x + dx < w and 0 <= y + dy < h:
                    opp_adj.add((x + dx, y + dy))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if abs(dx) + abs(dy) <= 2 and ok(ox + dx, oy + dy):
                opp_adj.add((ox + dx, oy + dy))

    best = None
    best_score = -10**18
    my_base = (sx, sy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        cell = (nx, ny)

        score = 0
        if cell in self_t:
            score += 40
        if cell in unclaimed:
            score += 120
            if cell in opp_adj:
                score -= 160
        if cell in opp_t:
            score -= 300
        if cell in opp_adj:
            score -= 40
        if resources:
            rx, ry = None, None
            for r in resources:
                if r and len(r) >= 2:
                    tx, ty = int(r[0]), int(r[1])
                    if 0 <= tx < w and 0 <= ty < h:
                        if rx is None or dist((tx, ty), cell) < dist((rx, ry), cell):
                            rx, ry = tx, ty
            if rx is not None:
                score -= 2 * dist((rx, ry), cell)

        score -= dist(my_base, cell) // 3
        if best is None or score > best_score:
            best = [dx, dy]
            best_score = score
    return best if best is not None else [0, 0]