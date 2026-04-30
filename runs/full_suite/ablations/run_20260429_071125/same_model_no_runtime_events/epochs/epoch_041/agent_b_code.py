def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w // 2), (h // 2)
        best_move = (0, 0)
        best_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            myd = kdist(nx, ny, tx, ty)
            oppd = kdist(nx, ny, ox, oy)
            key = (myd, -oppd, nx + ny)
            if best_key is None or key < best_key:
                best_key, best_move = key, (dx, dy)
        return [best_move[0], best_move[1]]

    best_r = None
    best_key = None
    for tx, ty in resources:
        myd = kdist(sx, sy, tx, ty)
        od = kdist(ox, oy, tx, ty)
        lead = od - myd
        can_take = myd <= od
        # Prefer taking earlier; otherwise deny by choosing resources where we're least worse.
        key = (0 if can_take else 1, -lead, myd, tx + ty)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (tx, ty)

    tx, ty = best_r
    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = kdist(nx, ny, tx, ty)
        oppd = kdist(nx, ny, ox, oy)
        # Primary: get closer to the chosen target; secondary: keep distance from opponent.
        key = (myd2, -oppd, abs(nx - tx) + abs(ny - ty))
        if best_key is None or key < best_key:
            best_key, best_move = key, (dx, dy)

    return [best_move[0], best_move[1]]