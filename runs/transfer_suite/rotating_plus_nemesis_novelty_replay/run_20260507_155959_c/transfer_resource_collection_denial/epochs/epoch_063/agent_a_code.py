def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # king distance (diagonal allowed)

    if not resources:
        cx, cy = w // 2, h // 2
        best = [0, 0]
        bestv = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                v = (dist(nx, ny, ox, oy), dist(nx, ny, cx, cy), nx, ny)
                if bestv is None or v < bestv:
                    bestv = v
                    best = [dx, dy]
        return best

    # Prefer resources where we can arrive earlier than the opponent; break ties by urgency/position.
    best_t = None
    best_key = None
    for x, y in resources:
        ds = dist(sx, sy, x, y)
        do = dist(ox, oy, x, y)
        # Row/col "sweep" pressure: if aligned, opponent often contests; prioritize our advantage there.
        aligned = (x == ox) or (y == oy)
        # Key: higher (do-ds) first. Then smaller ds. Then prefer lower coords deterministically.
        advantage = do - ds
        key = (advantage, -ds, -1 if aligned else 0, -((x + y) & 1), -x, -y)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (x, y)

    tx, ty = best_t
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    # Diagonal first if it helps; otherwise orthogonal; then stay.
    candidates.append((dx, dy))
    candidates.append((dx, 0))
    candidates.append((0, dy))
    candidates.append((0, 0))
    for adx in (-1, 1, 0):
        pass

    best = [0, 0]
    bestv = None
    for mdx, mdy in candidates:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Deterministically choose move that reduces our distance most while considering opponent distance.
        v = (dist(nx, ny, tx, ty), dist(nx, ny, ox, oy), nx, ny)
        if bestv is None or v < bestv:
            bestv = v
            best = [mdx, mdy]
    return [best[0], best[1]]