def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None  # (priority, ds, -do, tx, ty)
    for tx, ty in res:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer resources we can reach earlier; otherwise still prefer those we "beat" by margin.
        pri = 1 if ds < do else (0 if ds == do else -1)
        k = (pri, -(do - ds), ds, -do, tx, ty)
        # min over k: higher pri, smaller ds, larger do
        if best is None or k < best[0]:
            best = (k, (tx, ty))

    _, (tx, ty) = best
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(dx0, dy0), (dx0, 0), (0, dy0), (dx0, -dy0), (-dx0, dy0), (-dx0, 0), (0, -dy0), (0, 0), (-dx0, -dy0)]
    seen = set()
    cand = []
    for dx, dy in moves:
        if (dx, dy) in seen:
            continue
        seen.add((dx, dy))
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ds_next = cheb(nx, ny, tx, ty)
        do_next = cheb(ox, oy, tx, ty)
        # Tie-break deterministically: prioritize smaller ds_next, then larger opponent reach advantage.
        score = (ds_next, -(do_next - ds_next), abs(nx - tx) + abs(ny - ty), nx, ny)
        cand.append((score, [dx, dy]))
    if not cand:
        return [0, 0]
    cand.sort(key=lambda x: x[0])
    return cand[0][1]