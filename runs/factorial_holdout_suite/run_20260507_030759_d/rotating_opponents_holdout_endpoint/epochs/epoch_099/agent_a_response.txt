def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not resources:
        dx = 0 if sx == ox else (1 if ox > sx else -1)
        dy = 0 if sy == oy else (1 if oy > sy else -1)
        return [dx, dy]

    # pick best target deterministically
    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not valid(rx, ry):
            continue
        st = cheb(sx, sy, rx, ry)
        ot = cheb(ox, oy, rx, ry)
        # prioritize strictly earlier; then maximize lead; then smaller our time; then deterministic tie-break by coords
        lead = ot - st
        key = (1 if st < ot else 0, lead, -st, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    # choose move that reduces our distance to target and doesn't hit obstacle
    options = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    bestk = None
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nt = cheb(nx, ny, tx, ty)
        to = cheb(nx, ny, ox, oy)
        # prefer smaller distance to target; then maximize opponent distance (avoid giving capture); then deterministic order by move
        k = (-nt, to, dx, dy)
        if bestk is None or k > bestk:
            bestk = k
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]