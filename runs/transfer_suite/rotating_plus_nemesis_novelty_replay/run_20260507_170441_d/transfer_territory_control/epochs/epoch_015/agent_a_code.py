def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources", []) or []
    targets = []
    for p in resources:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in blocked:
                targets.append((x, y))
        except:
            pass

    cx, cy = w // 2, h // 2
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if targets:
        tx, ty = min(targets, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        tx, ty = cx, cy

    best = (0, 0)
    best_score = -10**18
    order = dirs

    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d_to_t = abs(nx - tx) + abs(ny - ty)
        d_to_o = abs(nx - ox) + abs(ny - oy)
        score = -d_to_t + 0.25 * d_to_o
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best == (0, 0):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]