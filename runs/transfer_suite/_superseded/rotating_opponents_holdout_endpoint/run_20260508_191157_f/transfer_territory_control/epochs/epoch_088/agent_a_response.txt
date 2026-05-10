def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    oppT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    opp_list = list(oppT) if oppT else []
    obst_list = list(obstacles)

    opts = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            opts.append((dx, dy, nx, ny))

    if not opts:
        return [0, 0]

    def nearest_dist_to(points, x, y, default=999):
        if not points:
            return default
        best = default
        for px, py in points:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    best = None
    best_score = None
    for dx, dy, nx, ny in opts:
        in_opp = (nx, ny) in oppT
        adj_unclaimed = 0
        adj_self = 0
        for ax, ay in neighbors(nx, ny):
            if (ax, ay) in unclaimed:
                adj_unclaimed += 1
            elif (ax, ay) in selfT:
                adj_self += 1
        score = 0.0
        score += 1.2 if in_opp else 0.0
        score += 0.35 * adj_unclaimed
        score += 0.12 * adj_self
        score -= 0.03 * nearest_dist_to(opp_list, nx, ny, default=10)
        score -= 0.01 * nearest_dist_to(obst_list, nx, ny, default=10)

        # Deterministic tie-break: prefer smaller dx then smaller dy when scores match
        key = (score, -dx, -dy)  # higher score, then prefer larger dx negative? deterministic
        if best is None or key > best:
            best = key
            best_score = score
            best_move = [dx, dy]

    return best_move