def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    self_terr = observation.get("self_territory") or []
    self_set = set()
    for a, b in self_terr:
        x, y = int(a), int(b)
        if 0 <= x < w and 0 <= y < h:
            self_set.add((x, y))
    if not self_set:
        self_set = {(sx, sy)}

    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set()
    for a, b in unclaimed:
        x, y = int(a), int(b)
        if 0 <= x < w and 0 <= y < h:
            un_set.add((x, y))

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    targets = set()
    for x, y in self_set:
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if (nx, ny) in un_set:
                targets.add((nx, ny))
    if not targets:
        targets = un_set
    if not targets:
        targets = {(ox, oy)}

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_score = -10**18
    best_t = 10**18
    for dx, dy in [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = min(md(nx, ny, tx, ty) for tx, ty in targets)
        do = md(nx, ny, ox, oy)
        score = -d + 0.02 * do
        if score > best_score or (score == best_score and d < best_t):
            best_score = score
            best_t = d
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]