def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def md(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0: d1 = -d1
        d2 = ay - by
        if d2 < 0: d2 = -d2
        return d1 + d2

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_r = None
        best_adv = None
        best_my = None
        best_key = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            oppd = md(ox, oy, rx, ry)
            adv = oppd - myd  # maximize our advantage
            key = (-(adv), myd, rx, ry)  # deterministic tie-break
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
                best_adv = adv
                best_my = myd
        tx, ty = best_r
    else:
        tx, ty = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)

    curd = md(sx, sy, tx, ty)
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = md(nx, ny, tx, ty)

        # estimate opponent's ability to steal chosen target next
        oppd = md(ox, oy, tx, ty)
        adv = oppd - myd

        bonus = 0
        if resources and (nx, ny) in resources:
            bonus = 100000
        if resources:
            # slight preference for reducing our distance when advantage is equal
            if adv > (best_adv if best_adv is not None else 0):
                bonus += 2000

        score = (bonus + adv * 1000 - myd * 10 - (myd == 0) * 50000, -myd, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]