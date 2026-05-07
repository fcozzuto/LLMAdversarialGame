def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    def xy(v):
        try:
            return (int(v[0]), int(v[1]))
        except:
            return (0, 0)

    sx, sy = xy(observation.get("self_position"))
    ox, oy = xy(observation.get("opponent_position"))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = xy(p)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = xy(r)
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    midx = (w - 1) / 2.0
    midy = (h - 1) / 2.0

    best_t = None
    best_s = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        if myd == 0:
            s = 10_000 - (abs(tx - midx) + abs(ty - midy)) * 0.01
        else:
            lead = opd - myd  # positive means we're closer than opponent
            center = (abs(tx - midx) + abs(ty - midy))
            s = lead * 1000 - myd * 10 - center * 0.1
        if best_s is None or s > best_s:
            best_s = s
            best_t = (tx, ty)

    tx, ty = best_t

    best_move = (0, 0)
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx + dx
            ny = sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Prefer reducing our distance to target; break ties by improving relative lead, then deterministically by dx,dy order
            val = (myd, -(opd - myd), abs(dx), abs(dy), dx, dy)
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]