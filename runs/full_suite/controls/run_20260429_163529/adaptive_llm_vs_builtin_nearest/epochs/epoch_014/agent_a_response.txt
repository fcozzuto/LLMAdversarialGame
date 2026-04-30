def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = observation.get("resources") or []
    if not resources:
        # default: move towards center
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def resource_best_for_move(nx, ny):
        # prefer resources we can reach earlier; if not, still minimize opponent lead
        best = None
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not inb(rx, ry) and (rx, ry) not in obs:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive => we are earlier
            # deterministic tie-break: closer overall when contest is tight
            key = (adv, -ds, (rx * 13 + ry * 17) % 19)
            if best is None or key > best:
                best = key
        if best is None:
            return (-10**9, 0)
        return best

    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        key = resource_best_for_move(nx, ny)
        # small secondary: keep opponent distance from decreasing too fast
        oppd = cheb(nx, ny, ox, oy)
        full = (key[0], key[1], -oppd, (nx * 7 + ny * 11) % 23)
        if best_key is None or full > best_key:
            best_key = full
            best_move = [dx, dy]

    if best_key is None:
        return [0, 0]
    return best_move