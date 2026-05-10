def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_list:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    if not resources:
        return [0, 0]

    # Pick resource where we are relatively closer than opponent (more "control").
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not (0 <= rx < w and 0 <= ry < h):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = (do - ds, -ds, rx, ry)  # maximize do-ds, then minimize ds, then coords
        if best is None or score > best[0]:
            best = (score, (rx, ry))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    # Choose best immediate move that stays valid and reduces distance to target.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                candidates.append((dx, dy, cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy)))
    if not candidates:
        return [0, 0]

    # Prefer moves minimizing distance to target; tie-break by also increasing opponent distance.
    bestm = None
    for dx, dy, dt, do in candidates:
        key = ( -dt, do, -dx, -dy)  # maximize (-dt), then maximize do, then deterministic
        if bestm is None or key > bestm[0]:
            bestm = (key, (dx, dy))
    return [int(bestm[1][0]), int(bestm[1][1])]