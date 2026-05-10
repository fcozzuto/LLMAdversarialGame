def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    self_t = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) == 2:
            self_t.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) == 2:
            unclaimed.append((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    def score_cell(cell):
        x, y = cell
        s = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in self_t:
                s += 5
        s -= abs(x - ox) + abs(y - oy)
        s -= (abs(x - sx) + abs(y - sy)) * 0.1
        return s

    targets = []
    if self_t and unclaimed:
        for c in unclaimed:
            x, y = c
            if any((x + dx, y + dy) in self_t for dx, dy in dirs):
                targets.append(c)
    if not targets:
        targets = unclaimed[:10] if unclaimed else [(ox, oy)]

    best = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Prefer moving closer to best target, then closer to opponent
        if targets:
            min_t = None
            for t in targets:
                tx, ty = t
                d = abs(tx - nx) + abs(ty - ny)
                if min_t is None or d < min_t:
                    min_t = d
            sc = -min_t + (-(abs(nx - ox) + abs(ny - oy)) * 0.01)
        else:
            sc = -(abs(nx - ox) + abs(ny - oy))
        if best is None or sc > best:
            best = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]