def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def blocked(x, y):
        return (x, y) in obstacles

    if not resources:
        best = None
        best_sc = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            min_d = 10**9
            for odx, ody in deltas:
                tx, ty = ox + odx, oy + ody
                if inb(tx, ty) and not blocked(tx, ty):
                    d = man(nx, ny, tx, ty)
                    if d < min_d:
                        min_d = d
            sc = (min_d, man(nx, ny, ox, oy) * -1, -(abs(dx) + abs(dy)))
            if best_sc is None or sc > best_sc:
                best_sc, best = sc, [dx, dy]
        return best if best is not None else [0, 0]

    best = [0, 0]
    best_sc = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        best_adv = -10**9
        min_self_d = 10**9
        min_opp_d = 10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer (better)
            if adv > best_adv:
                best_adv = adv
            if sd < min_self_d:
                min_self_d = sd
            if od < min_opp_d:
                min_opp_d = od
        sc = (best_adv, -min_self_d, min_opp_d, -(abs(dx) + abs(dy)))
        if best_sc is None or sc > best_sc:
            best_sc, best = sc, [dx, dy]
    return best