def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Preselect candidate targets.
    my_better = []
    for rx, ry in resources:
        dm = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        if dm <= do:
            my_better.append((rx, ry))
    targets = my_better if my_better else resources

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Resource progress: prefer reducing distance to closest viable target.
        mind = 10**9
        best_t = None
        for rx, ry in targets:
            d = md(nx, ny, rx, ry)
            if d < mind:
                mind = d
                best_t = (rx, ry)

        # Tie-breaker / blocking: if a particular resource exists, measure opponent relative position to it.
        block = 0.0
        if best_t is not None:
            rx, ry = best_t
            my_d_after = md(nx, ny, rx, ry)
            op_d = md(ox, oy, rx, ry)
            # Positive if we stay at least as close; negative if opponent is closer.
            block = (op_d - my_d_after) * 0.15

        # Slight center bias to avoid stalling near corners.
        center = -(abs(nx - cx) + abs(ny - cy)) * 0.02

        score = (-mind) + block + center

        # Deterministic tie-break: smallest |dx|+|dy|, then lexicographic.
        if best is None or score > best_score or (score == best_score and (abs(dx) + abs(dy), dx, dy) < (abs(best[0]) + abs(best[1]), best[0], best[1])):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]