def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def score_move(dx, dy, tx, ty):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**9
        dtx = abs(nx - tx) + abs(ny - ty)
        dop = abs(nx - ox) + abs(ny - oy)
        resbias = 0
        if observation.get("resources"):
            resbias = -dtx
        else:
            resbias = -(dtx + 0.1 * dop)
        return 1000000 - dtx - dop * 0.05 + resbias * 0.01

    resources = observation.get("resources") or []
    if resources:
        tx, ty = min(resources, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
        best = max((score_move(dx, dy, tx, ty), i, dx, dy) for i, (dx, dy) in enumerate(dirs))
        return [best[2], best[3]]

    unclaimed = observation.get("unclaimed_cells") or None
    if unclaimed:
        unclaimed_set = set(map(tuple, unclaimed))
    else:
        unclaimed_set = set()

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    if self_terr and unclaimed_set:
        targets = []
        for x, y in self_terr:
            for dx, dy in dirs[:4]:
                nx, ny = x + dx, y + dy
                if (nx, ny) in unclaimed_set and inb(nx, ny) and (nx, ny) not in obstacles:
                    targets.append((nx, ny))
        if targets:
            tx, ty = min(targets, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
            best = max((score_move(dx, dy, tx, ty), i, dx, dy) for i, (dx, dy) in enumerate(dirs))
            return [best[2], best[3]]

    cx, cy = w // 2, h // 2
    best = None
    for i, (dx, dy) in enumerate(dirs):
        s = score_move(dx, dy, cx, cy)
        if best is None or s > best[0]:
            best = (s, i, dx, dy)
    return [best[2], best[3]]