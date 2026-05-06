def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                ob.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    res = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                res.append((rx, ry))
    if not res:
        # deterministic fallback: move toward center while avoiding obstacles
        best = (0, 0, 10**9, 10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            cen = md(nx, ny, cx, cy)
            k = (0, -cen, cen, 0)
            if k[1] < best[1] or (k[1] == best[1] and k[2] < best[2]):
                best = (dx, dy, k[2], k[3])
        return [best[0], best[1]]

    opp_now = [(md(ox, oy, rx, ry), rx, ry) for (rx, ry) in res]

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_best = 10**9
        adv_best = -10**9
        for od, rx, ry in opp_now:
            sd = md(nx, ny, rx, ry)
            # aim to be closer than opponent to a resource (advantage), but also prefer closer overall
            adv = (od - sd)
            if adv > adv_best or (adv == adv_best and sd < self_best):
                adv_best = adv
                self_best = sd
        # tie-break: prefer smaller distance to center, then lexical move order
        key = (adv_best, -self_best, -md(nx, ny, cx, cy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]