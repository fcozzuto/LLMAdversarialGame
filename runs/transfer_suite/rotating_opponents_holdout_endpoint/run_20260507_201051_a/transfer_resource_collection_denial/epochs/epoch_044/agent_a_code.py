def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Choose a target resource where we are likely to arrive first.
    best_r = None
    best_t = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        margin = do - ds  # positive means we are closer
        # Prefer (1) beating opponent, (2) larger margin, (3) shorter own distance, (4) deterministic tie by coords.
        t = (0 if margin >= 1 else 1, -margin, ds, rx, ry)
        if best_t is None or t < best_t:
            best_t = t
            best_r = (rx, ry)

    tx, ty = best_r

    # Greedily pick the move that improves capture prospects and keeps safe.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ds2 = man(nx, ny, tx, ty)
        do2 = man(ox, oy, tx, ty)
        margin2 = do2 - ds2
        # Higher is better: winning margin, then being closer; mild penalty for moving away from resources generally handled by ds2.
        score = (margin2 >= 1, margin2, -ds2, -abs((nx + ny) - (sx + sy)), tx, ty, nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move