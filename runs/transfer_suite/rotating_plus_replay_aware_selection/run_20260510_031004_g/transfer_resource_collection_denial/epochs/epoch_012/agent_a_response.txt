def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res = [(int(p[0]), int(p[1])) for p in resources]

    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        best_adv = -10**9
        best_myd = 10**9
        best_opd = 10**9
        for tx, ty in res:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            adv = opd - myd  # higher => I can contest/arrive earlier or closer than opponent
            # If opponent is closer, still prefer targets where I reduce the gap most (adv closer to 0)
            if adv > best_adv or (adv == best_adv and (myd < best_myd or (myd == best_myd and opd < best_opd))):
                best_adv, best_myd, best_opd = adv, myd, opd
        key = (best_adv, -best_myd, -best_opd, dx, dy)
        if best_key is None or key > best_key:
            best_key, best_move = key, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]