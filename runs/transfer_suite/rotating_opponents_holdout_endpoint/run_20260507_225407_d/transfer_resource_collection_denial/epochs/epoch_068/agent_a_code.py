def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))
        except Exception:
            pass

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    resources_raw = observation.get("resources") or []
    resources = []
    for p in resources_raw:
        try:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))
        except Exception:
            pass

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not ok(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        bestm, bestv = [0, 0], -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -man(nx, ny, tx, ty)
            if v > bestv:
                bestv, bestm = v, [dx, dy]
        return bestm

    bestm, bestv = [0, 0], -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        best_local = 10**18
        score = -10**18
        for rx, ry in resources:
            d_self = man(nx, ny, rx, ry)
            if d_self < best_local:
                best_local = d_self
            d_opp = man(ox, oy, rx, ry)
            # Prefer resources closer to self, and where self is "ahead" of opponent (deny).
            # Small bias toward cells closer to center to reduce dithering.
            v = (-10 * d_self) + (2 * (d_opp - d_self)) - (man(nx, ny, w // 2, h // 2) * 0.1)
            if v > score:
                score = v

        # Prefer shorter distance overall if scores tie.
        score -= best_local * 0.01
        if score > bestv:
            bestv, bestm = score, [dx, dy]

    return bestm