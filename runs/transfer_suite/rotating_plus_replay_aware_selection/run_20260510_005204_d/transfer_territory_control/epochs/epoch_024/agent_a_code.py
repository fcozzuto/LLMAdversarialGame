def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    unclaimed = observation.get("unclaimed_cells")
    resources = observation.get("resources")
    if unclaimed:
        cells = []
        for p in unclaimed:
            if not p or len(p) < 2: 
                continue
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                cells.append((x, y))
        target = None
        best = None
        for x, y in cells[:2000]:
            ds = abs(x - sx) + abs(y - sy)
            do = abs(x - ox) + abs(y - oy)
            sc = (do - ds) - 0.01 * (abs(x - (w - 1) // 2) + abs(y - (h - 1) // 2))
            if best is None or sc > best:
                best, target = sc, (x, y)
    else:
        cells = []
        if resources:
            for p in resources:
                if not p or len(p) < 2:
                    continue
                x, y = int(p[0]), int(p[1])
                if inb(x, y) and (x, y) not in obstacles:
                    cells.append((x, y))
        target = None
        best = None
        for x, y in (cells if cells else [(sx, sy)]):
            ds = abs(x - sx) + abs(y - sy)
            sc = -ds - 0.001 * abs(x - ox) - 0.001 * abs(y - oy)
            if best is None or sc > best:
                best, target = sc, (x, y)
        if target is None:
            target = ((w - 1) // 2, (h - 1) // 2)
    tx, ty = target
    best_d = None
    best_step = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_step):
            best_d = d
            best_step = (dx, dy)
    if best_step is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [int(dx), int(dy)]
        return [0, 0]
    return [int(best_step[0]), int(best_step[1])]