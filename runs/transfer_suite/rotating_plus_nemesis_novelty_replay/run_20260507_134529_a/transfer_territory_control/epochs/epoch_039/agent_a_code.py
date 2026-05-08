def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    unclaimed_list = observation.get("unclaimed_cells") or []
    target = None
    best = None

    # Deterministic candidate scan: first N unclaimed cells in provided order.
    N = 30
    for i, p in enumerate(unclaimed_list[:N]):
        if not (isinstance(p, (list, tuple)) and len(p) >= 2):
            continue
        x, y = int(p[0]), int(p[1])
        if not inb(x, y) or (x, y) in obstacles:
            continue
        du = man(sx, sy, x, y)
        do = man(ox, oy, x, y)
        # Prefer cells far from opponent while reachable.
        sc = do * 2 - du
        if best is None or sc > best:
            best = sc
            target = (x, y)

    if target is None:
        target = (w // 2, h // 2)
        if target in obstacles:
            target = (sx, sy)

    tx, ty = target
    best_move = None
    best_d = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        if best_d is None or d < best_d:
            best_d = d
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move