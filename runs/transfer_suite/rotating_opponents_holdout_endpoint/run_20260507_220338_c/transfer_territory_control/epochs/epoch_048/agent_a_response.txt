def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    self_set = set()
    opp_set = set()
    unclaimed_set = set()
    for p in self_t:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            self_set.add((int(p[0]), int(p[1])))
    for p in opp_t:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            opp_set.add((int(p[0]), int(p[1])))
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            unclaimed_set.add((int(p[0]), int(p[1])))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    tx, ty = (ox + sx) / 2.0, (oy + sy) / 2.0  # cut-off point

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_count(x, y, S):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in S:
                    c += 1
        return c

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        score = 0.0

        if (nx, ny) in opp_set:
            score += 120.0
        if (nx, ny) in unclaimed_set:
            score += 22.0
        if (nx, ny) in self_set:
            score += 8.0

        score += 6.0 * adj_count(nx, ny, self_set)
        score += 3.0 * adj_count(nx, ny, opp_set)

        d_center = abs(nx - cx) + abs(ny - cy)
        d_center_now = abs(sx - cx) + abs(sy - cy)
        score += 4.0 * (d_center_now - d_center)

        d_cut = abs(nx - tx) + abs(ny - ty)
        d_cut_now = abs(sx - tx) + abs(sy - ty)
        score += 3.5 * (d_cut_now - d_cut)

        if dx == 0 and dy == 0:
            score -= 1.5

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move