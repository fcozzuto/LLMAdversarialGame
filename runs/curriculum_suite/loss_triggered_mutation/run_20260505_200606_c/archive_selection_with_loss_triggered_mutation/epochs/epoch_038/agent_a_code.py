def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def edge_bias(x, y):
        # prefer resources not too trapped near center? keep slight edge attraction
        return min(x, w - 1 - x, y, h - 1 - y)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            adv = opd - myd
            # race win first, then closer; mild edge preference for long-term safety
            key = (adv * 8 - myd * 2 + (edge_bias(rx, ry) * 0.01))
            if best is None or key > best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    bestm = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd2 = md(nx, ny, tx, ty)
        # also hinder opponent if they are chasing same target-ish
        opd2 = md(ox, oy, tx, ty)
        # prefer decreasing my distance; if tied, choose move that increases opponent distance to same target
        sc = (-myd2) * 10 + (opd2 - myd2) * 0.01 + (dx * 0.001 + dy * 0.0001)
        if best_score is None or sc > best_score:
            best_score = sc
            bestm = (dx, dy)

    # Ensure return integers in {-1,0,1}
    dx, dy = bestm
    if dx < -1:
        dx = -1
    if dx > 1:
        dx = 1
    if dy < -1:
        dy = -1
    if dy > 1:
        dy = 1
    return [int(dx), int(dy)]