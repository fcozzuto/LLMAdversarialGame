def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(ax, ay, bx, by):
        return max(abs(ax - bx), abs(ay - by))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    best = None
    best_score = -10**9

    # Prefer approaching closest resource, but also avoid stepping into opponent's immediate zone
    target = None
    if resources:
        # choose nearest resource deterministically
        min_d = None
        for (rx, ry) in resources:
            d = dist(sx, sy, rx, ry)
            if min_d is None or d < min_d:
                min_d = d
                target = (rx, ry)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # basic scoring
        score = 0
        # distance to target
        if target is not None:
            d = dist(nx, ny, target[0], target[1])
            score -= d * 2  # strongly prefer closer
        # penalize moving onto opponent or near opponent to avoid capture
        odist = dist(nx, ny, ox, oy)
        if odist == 0:
            score -= 100  # avoid collision
        else:
            score -= max(0, 2 - odist)  # slight fear of nearby opponent
        # prefer staying if no better move
        if target is None:
            score += 1
        # tie-breaker: closer to center maybe
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= dist(nx, ny, int(cx), int(cy))
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        # fallback to staying
        return [0, 0]
    return [best[0], best[1]]