def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def cd(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if resources:
        best_move = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            best_for_move = None
            best_score = None
            for rx, ry in resources:
                sd = cd(nx, ny, rx, ry)
                od = cd(ox, oy, rx, ry)
                adv = od - sd  # positive means we are closer
                # prefer grabbing sooner, then winning the race
                key = (adv, -sd, -((rx + ry) & 3))
                if best_for_move is None or key > best_for_move:
                    best_for_move = key
                    best_score = adv
            # also include distance to closest resource for tie breaking
            closest = min(cd(nx, ny, r[0], r[1]) for r in resources)
            overall = (best_for_move[0], best_for_move[1], -closest, dx, dy)
            if best_key is None or overall > best_key:
                best_key = overall
                best_move = [dx, dy]
        return best_move

    # No resources visible: move to a strategic corner/intercept point relative to opponent
    tx = 0 if ox >= w // 2 else w - 1
    ty = h - 1 if oy < h // 2 else 0
    best = None
    bestd = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d = cd(nx, ny, tx, ty)
        key = (-(d), dx, dy)
        if bestd is None or key > bestd:
            bestd = key
            best = [dx, dy]
    return best