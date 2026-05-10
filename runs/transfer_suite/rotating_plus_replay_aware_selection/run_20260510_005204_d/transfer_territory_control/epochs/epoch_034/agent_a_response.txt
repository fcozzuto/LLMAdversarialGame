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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    unclaimed_list = list(unclaimed)
    def nearest_unclaimed_dist(x, y):
        if not unclaimed_list:
            return 0
        best = 10**9
        for ux, uy in unclaimed_list:
            d = abs(ux - x) + abs(uy - y)
            if d < best:
                best = d
        return best

    def adj_unclaimed_count(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                cnt += 1
        return cnt

    best_move = (0, 0)
    best_score = -10**18
    sx_dist_corner = abs(sx - 0) + abs(sy - 0)  # for tie-break determinism
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_terr:
            score += 18 + 2 * adj_unclaimed_count(nx, ny)
        elif (nx, ny) in unclaimed:
            score += 14 + 3 * adj_unclaimed_count(nx, ny)
        elif (nx, ny) in self_terr:
            score += 3
        else:
            score += 0

        # Prefer pushing into unclaimed regions (closer to nearest unclaimed)
        nd = nearest_unclaimed_dist(nx, ny)
        score += 2.0 / (1 + nd)

        # Keep pressure toward center (reduces edge trapping)
        score += -0.01 * (abs(nx - cx) + abs(ny - cy))

        # Deterministic tie-break: slight preference by move order
        score += -0.001 * (dx * 7 + dy * 3)

        # Another deterministic bias to keep from oscillating exactly at start corner
        score += -0.0005 * abs((nx - 0) + (ny - 0) - sx_dist_corner)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]