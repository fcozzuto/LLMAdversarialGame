def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    ax, ay = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    ax, ay = int(ax), int(ay)
    ox, oy = int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = observation.get("obstacles") or []
    blocked = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    target = observation.get("unclaimed_cells") or observation.get("resources") or []
    targets = []
    for p in target:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in blocked:
                targets.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if targets:
        best = None
        tx = ty = None
        for x, y in targets:
            d = abs(x - ax) + abs(y - ay)
            if best is None or d < best or (d == best and (x, y) < (tx, ty)):
                best = d
                tx, ty = x, y
        cx = 0 if tx == ax else (1 if tx > ax else -1)
        cy = 0 if ty == ay else (1 if ty > ay else -1)
        desired = (cx, cy)
    else:
        dx = 0 if ox == ax else (1 if ox > ax else -1)
        dy = 0 if oy == ay else (1 if oy > ay else -1)
        desired = (dx, dy)

    best_dir = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        score = 0
        if targets:
            score = abs(tx - nx) + abs(ty - ny)
            score += (abs(ox - nx) + abs(oy - ny)) * 0.01
        else:
            score = abs(nx - (ax + desired[0])) + abs(ny - (ay + desired[1]))
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_dir):
            best_score = score
            best_dir = (dx, dy)

    if best_dir is None:
        for dx, dy in dirs:
            nx, ny = ax + dx, ay + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                return [dx, dy]
        return [0, 0]
    return [int(best_dir[0]), int(best_dir[1])]