def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick a target where I'm relatively closer than the opponent.
    target = None
    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        score = (od - myd, -myd)  # maximize (od-myd), then minimize myd
        if best is None or score > best:
            best = score
            target = (rx, ry)
    if target is None:
        return [0, 0]

    tx, ty = target
    curd = cheb(sx, sy, tx, ty)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                nd = cheb(nx, ny, tx, ty)
                # Primary: get closer to target; Secondary: avoid getting too close to opponent
                # (keeps room for future choices / reduces being "boxed" by opponent).
                opp_sep = cheb(nx, ny, ox, oy)
                candidates.append(((nd, -opp_sep, -(abs(dx) + abs(dy))), (dx, dy)))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=False, key=lambda z: z[0])
    # Choose minimal nd; among ties prefer larger opp_sep and smaller move magnitude (deterministic).
    best_delta = None
    best_key = None
    for key, dlt in candidates:
        if best_key is None or key < best_key:
            best_key = key
            best_delta = dlt

    # If staying is as good as moving (or everything worsens), prefer staying.
    if best_delta is not None:
        dx, dy = best_delta
        nx, ny = sx + dx, sy + dy
        if cheb(nx, ny, tx, ty) >= curd and (0, 0) in [(0, 0)]:
            return [0, 0]
        return [dx, dy]
    return [0, 0]