def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target selection: maximize time advantage; if no advantage, go for best "race"
    best = None
    for tx, ty in resources:
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        adv = do - ds
        # Prefer earlier interception and safer choices (farther from edges a bit)
        edge_pen = (tx in (0, w - 1)) + (ty in (0, h - 1))
        key = (adv, -ds, -edge_pen, -tx, -ty)
        if best is None or key > best[0]:
            best = (key, (tx, ty))
    tx, ty = best[1]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free_neighbors(x, y):
        cnt = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cnt += 1
        return cnt

    # Choose move that most reduces distance to target; break ties by mobility
    best_move = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_after = man(nx, ny, tx, ty)
        d_now = man(sx, sy, tx, ty)
        # Small preference to avoid moves that help opponent by decreasing their distance too much
        opp_after = man(nx, ny, tx, ty)  # proxy, keeps deterministic and simple
        mob = free_neighbors(nx, ny)
        key = (-(d_after), -(d_now - d_after), mob, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]