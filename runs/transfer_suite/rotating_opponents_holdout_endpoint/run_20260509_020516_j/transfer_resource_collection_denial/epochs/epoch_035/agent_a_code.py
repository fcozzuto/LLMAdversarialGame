def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", None) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", None) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_for_move(nx, ny):
        best = None
        for tx, ty in resources:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            if sd == 0:
                score = (-10**9, 0, 0, tx, ty)  # immediately grab if possible
            else:
                score = (sd - od, sd, od, tx, ty)
            if best is None or score < best:
                best = score
        return best

    chosen = None
    chosen_dir = (0, 0)
    # Deterministic tie-break: prefer smaller dx, then smaller dy among equal score.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = best_for_move(nx, ny)
        key = (score[0], score[1], score[2], score[3], score[4], dx, dy)
        if chosen is None or key < chosen:
            chosen = key
            chosen_dir = (dx, dy)

    if chosen is None:
        return [0, 0]
    return [int(chosen_dir[0]), int(chosen_dir[1])]