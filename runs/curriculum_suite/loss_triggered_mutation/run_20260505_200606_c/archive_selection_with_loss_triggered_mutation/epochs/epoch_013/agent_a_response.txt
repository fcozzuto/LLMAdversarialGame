def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return (x, y) not in obstacles

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    cx0 = (w - 1) / 2.0
    cy0 = (h - 1) / 2.0

    def center_score(x, y):
        dx = x - cx0
        dy = y - cy0
        return -(dx * dx + dy * dy)

    if not resources:
        best = [-10**18, 0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or not ok(nx, ny):
                continue
            v = man(nx, ny, ox, oy) * 10 + center_score(nx, ny)
            if v > best[0] or (v == best[0] and (dx, dy) < (best[1], best[2])):
                best = [v, dx, dy]
        return [best[1], best[2]]

    best = [-10**18, 0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or not ok(nx, ny):
            continue
        # Look one step: choose the resource we create the strongest relative advantage for.
        best_adv = -10**18
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - self_d
            # Prefer not just advantage but also progress; slight center bias helps break ties.
            v = adv * 1000 - self_d * 2 + center_score(nx, ny) * 0.05
            if v > best_adv:
                best_adv = v
        # Avoid stepping into immediate opponent pressure: if opponent is very close, back off slightly.
        pressure = man(nx, ny, ox, oy)
        v = best_adv + (pressure * 0.5)
        if v > best[0] or (v == best[0] and (dx, dy) < (best[1], best[2])):
            best = [v, dx, dy]
    return [best[1], best[2]]