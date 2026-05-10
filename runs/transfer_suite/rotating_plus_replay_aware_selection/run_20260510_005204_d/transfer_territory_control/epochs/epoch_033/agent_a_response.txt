def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_unclaimed_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    def cell_value(x, y):
        v = 0
        if (x, y) in opp_terr:
            v += 4
        elif (x, y) in unclaimed:
            v += 6
        elif (x, y) in self_terr:
            v += 1
        else:
            v += 0
        v += 2 * adj_unclaimed_count(x, y)
        # Prefer expanding away from the exact corner line if tied: drive toward center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(x - cx) + abs(y - cy)
        v += -0.05 * dist_center
        # Small penalty if we're adjacent to obstacles (less room).
        near_obs = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obstacles:
                near_obs += 1
        v += -0.2 * near_obs
        return v

    best = (float("-inf"), 0, 0)
    for dx, dy in moves:
        x1, y1 = sx + dx, sy + dy
        if not inb(x1, y1):
            continue
        # 1-ply lookahead for better frontier capture.
        best2 = float("-inf")
        for ddx, ddy in moves:
            x2, y2 = x1 + ddx, y1 + ddy
            if not inb(x2, y2):
                continue
            vv = cell_value(x2, y2)
            if vv > best2:
                best2 = vv
        score = 0.7 * cell_value(x1, y1) + 0.3 * best2
        if score > best[0]:
            best = (score, dx, dy)

    if best[0] == float("-inf"):
        return [0, 0]
    return [int(best[1]), int(best[2])]