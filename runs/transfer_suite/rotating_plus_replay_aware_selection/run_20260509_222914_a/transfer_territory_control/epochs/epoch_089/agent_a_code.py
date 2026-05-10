def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])

    op = observation.get("opponent_position", [sx, sy])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_ter = set()
    for p in observation.get("self_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_ter.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist2(x, y, tx, ty):
        dx, dy = tx - x, ty - y
        return dx * dx + dy * dy

    if max(abs(ox - sx), abs(oy - sy)) <= 1:
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not cell_free(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            if best is None or d < best[0]:
                best = (d, [dx, dy])
        return best[1] if best else [0, 0]

    target = (ox, oy)
    best_dist = dist2(sx, sy, ox, oy)

    if resources:
        for tx, ty in resources:
            d = dist2(sx, sy, tx, ty)
            if d < best_dist:
                best_dist, target = d, (tx, ty)

    if not resources and unclaimed and self_ter:
        frontier = []
        s = self_ter
        for tx, ty in unclaimed:
            if any((tx + ax, ty + ay) in s for ax in (-1, 0, 1) for ay in (-1, 0, 1) if not (ax == 0 and ay == 0)):
                frontier.append((tx, ty))
        if frontier:
            for tx, ty in frontier:
                d = dist2(sx, sy, tx, ty)
                if d < best_dist:
                    best_dist, target = d, (tx, ty)
    elif not resources and unclaimed:
        for tx, ty in unclaimed:
            d = dist2(sx, sy, tx, ty)
            if d < best_dist:
                best_dist, target = d, (tx, ty)

    tx, ty = target
    best_move = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not cell_free(nx, ny):
            continue
        d = dist2(nx, ny, tx, ty)
        if best_score is None or d < best_score:
            best_score = d
            best_move = [dx, dy]
    return best_move if best_move else [0, 0]