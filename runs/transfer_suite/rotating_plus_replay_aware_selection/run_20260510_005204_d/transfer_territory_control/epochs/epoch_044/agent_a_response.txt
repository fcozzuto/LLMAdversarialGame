def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_count(x, y, target):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny) and (nx, ny) in target:
                c += 1
        return c

    def cell_score(x, y):
        v = 0
        if (x, y) in opp_terr:
            v += 18
        elif (x, y) in unclaimed:
            v += 12
        elif (x, y) in self_terr:
            v += 3
        v += 3 * adj_count(x, y, unclaimed)
        v += 2 * adj_count(x, y, opp_terr)
        # Prefer pushing toward the center to reduce edge sniping effectiveness
        v -= 0.08 * (abs(x - cx) + abs(y - cy))
        return v

    def apply_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            return sx, sy
        return nx, ny

    best = None
    for dx, dy in moves:
        x1, y1 = apply_move(dx, dy)
        # 2-step greedy lookahead for deterministic improvement
        best2 = -10**9
        for dx2, dy2 in moves:
            x2, y2 = x1 + dx2, y1 + dy2
            if not ok(x2, y2):
                x2, y2 = x1, y1
            s2 = cell_score(x2, y2)
            if s2 > best2:
                best2 = s2
        score = cell_score(x1, y1) + 0.65 * best2
        key = (score, -abs(dx) - abs(dy), -dx, -dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])
    return best[1]