def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set()
    for c in (observation.get("unclaimed_cells") or []):
        if c is not None and len(c) >= 2:
            unclaimed.add((int(c[0]), int(c[1])))

    opp_t = set()
    for c in (observation.get("opponent_territory") or []):
        if c is not None and len(c) >= 2:
            opp_t.add((int(c[0]), int(c[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def neigh(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    targets = []
    for r in (observation.get("resources") or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y) and (x, y) != (ox, oy):
                targets.append((x, y))
    if not targets:
        for c in unclaimed:
            if free(c[0], c[1]) and c != (ox, oy):
                targets.append(c)

    if targets:
        best_t = min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
    else:
        best_t = (ox, oy)

    best_move = [0, 0]
    best_score = -10**18
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        adj_unclaimed = 0
        adj_opp = 0
        for ax, ay in neigh(nx, ny):
            if (ax, ay) in unclaimed:
                adj_unclaimed += 1
            if (ax, ay) in opp_t:
                adj_opp += 1
        dist_to_target = abs(best_t[0] - nx) + abs(best_t[1] - ny)
        dist_to_opp = abs(ox - nx) + abs(oy - ny)
        edge_boost = 1 if (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1) else 0
        score = 3.0 * adj_unclaimed + 2.0 * adj_opp + 0.2 * edge_boost - 0.05 * dist_to_target + 0.03 * dist_to_opp
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]