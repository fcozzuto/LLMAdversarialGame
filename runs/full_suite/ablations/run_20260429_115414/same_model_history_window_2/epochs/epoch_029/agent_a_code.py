def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    if resources:
        tx, ty = min(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer getting closer to target relative to opponent
            score = ds - do
            if best is None or score < best[0]:
                best = (score, dx, dy)
        if best is not None:
            return [best[1], best[2]]
    # No valid resource move (or no resources): go toward center while keeping away from opponent
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dc = cheb(nx, ny, cx, cy)
        dp = cheb(nx, ny, ox, oy)
        score = dc - 0.5 * dp
        if best is None or score < best[0]:
            best = (score, dx, dy)
    if best is None:
        return [0, 0]
    return [best[1], best[2]]