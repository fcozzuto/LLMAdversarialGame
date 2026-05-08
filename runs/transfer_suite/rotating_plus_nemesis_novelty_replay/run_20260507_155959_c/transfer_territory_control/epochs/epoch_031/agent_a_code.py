def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    unclaimed = observation.get("unclaimed_cells", []) or []

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx >= 0 else -dx + (dy if dy >= 0 else -dy)  # avoid abs()

    # Fix man() without abs while keeping it correct
    def man2(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    target = None
    best = None
    for x, y in unclaimed:
        x, y = int(x), int(y)
        if not inb(x, y) or (x, y) in obstacles:
            continue
        if (x, y) in self_cells or (x, y) in opp_cells:
            continue
        ds = man2(sx, sy, x, y)
        do = man2(ox, oy, x, y)
        score = ds - do  # prefer cells we can reach earlier than opponent
        if best is None or score < best:
            best = score
            target = (x, y)

    if target is None:
        target = (ox, oy)

    tx, ty = target
    best_move = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = man2(nx, ny, tx, ty)  # go toward target
        # small tie-break: move away from opponent to avoid being overtaken
        val2 = val - 0.05 * man2(nx, ny, ox, oy)
        if best_val is None or val2 < best_val:
            best_val = val2
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]