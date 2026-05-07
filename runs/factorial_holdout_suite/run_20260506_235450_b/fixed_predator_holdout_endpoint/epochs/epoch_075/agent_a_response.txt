def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    def clutter(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_key = None

    for tx, ty in res:
        my_d = md(sx, sy, tx, ty)
        opp_d = md(ox, oy, tx, ty)
        adv = opp_d - my_d  # positive if I'm closer
        cl = clutter(tx, ty)

        if my_d < opp_d:
            # Prioritize being closer; prefer decisive leads, then shorter travel, then less clutter.
            key = (1, adv, -my_d, -cl, -tx, -ty)
        else:
            # If I'm not closer to any, race the best-available (high opp_d - my_d, but with minimal opp_d).
            key = (0, adv, -(opp_d), -my_d, -cl, -tx, -ty)

        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Mild anti-loop: if moving diagonally overshoots around many obstacles near target, favor axis-aligned step.
    if dx != 0 and dy != 0 and (clutter(tx, ty) >= 4):
        if md(sx + dx, sy, tx, ty) <= md(sx, sy + dy, tx, ty):
            dy = 0
        else:
            dx = 0

    return [dx, dy]