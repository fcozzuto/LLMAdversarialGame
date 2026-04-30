def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a deterministic target: prefer larger opponent disadvantage and closer for self.
    best = None
    best_score = None
    for x, y in resources:
        ds = man(sx, sy, x, y)
        do = man(ox, oy, x, y)
        score = (do - ds) * 1000 - ds  # scalar; higher is better
        if best_score is None or score > best_score:
            best_score = score
            best = (x, y)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_eval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds = man(nx, ny, tx, ty)
        do = man(nx, ny, ox, oy)
        # Minimize distance to target; maximize opponent distance; deterministic tie-break by move order.
        ev = (ds, -do)
        if best_eval is None or ev < best_eval:
            best_eval = ev
            best_move = [dx, dy]

    return best_move