def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    resources = toset(observation.get("resources"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    myT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))

    targets = unclaimed | resources
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_target_dist(x, y):
        best = 10**9
        for tx, ty in targets:
            if (tx, ty) in obstacles:
                continue
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
        return best if best != 10**9 else None

    best_move = (0, 0)
    best_score = -10**18
    nd = nearest_target_dist(sx, sy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        d_t = nearest_target_dist(nx, ny)
        if d_t is not None:
            score += 2000 - 10 * d_t
            if (nx, ny) in targets:
                score += 1500
        if (nx, ny) in myT:
            score += 50
        if (nx, ny) in oppT:
            score -= 200

        # If no targets exist, drift toward opponent to contest
        if nd is None and not targets:
            score += - (abs(ox - nx) + abs(oy - ny))

        # Deterministic tie-breaker
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]