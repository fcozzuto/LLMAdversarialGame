def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))

    if not unclaimed and resources:
        unclaimed = set(resources)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_opp_dist(x, y):
        if not oppT:
            return 999
        best = 999
        for ax, ay in oppT:
            d = abs(ax - x) + abs(ay - y)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = -10**18
    best_move = (0, 0)

    d0c = abs(sx - cx) + abs(sy - cy)
    d0o = nearest_opp_dist(sx, sy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        is_uncl = (nx, ny) in unclaimed
        is_opp = (nx, ny) in oppT
        is_res = (nx, ny) in resources
        is_self = (nx, ny) in selfT

        dnc = abs(nx - cx) + abs(ny - cy)
        dno = nearest_opp_dist(nx, ny)

        score = 0.0
        score += 6.0 if is_uncl else 0.0
        score += 3.5 if is_res else 0.0
        score += 4.0 if is_opp else 0.0
        score += -0.7 if is_self else 0.0

        score += 1.2 * (d0c - dnc)  # closer to center
        score += 0.9 * (d0o - dno)  # closer to opponent territory

        # small tie-breaker to avoid staying still when alternatives exist
        if dx == 0 and dy == 0:
            score -= 0.25

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]