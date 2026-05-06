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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        best = (0, 0)
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -(md(nx, ny, cx, cy)) - 0.1 * md(nx, ny, ox, oy)
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    bestv = None
    base_center = md(sx, sy, cx, cy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        best_gain = -10**9
        best_deny = -10**9
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not valid(rx, ry):
                continue
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            gain = od - sd  # positive means we're closer than opponent would be at current turn
            if gain > best_gain:
                best_gain = gain
            # deny: if opponent is currently closer, move reduces their advantage by approaching that resource
            if od < sd:
                deny = sd - od  # smaller is better; convert to larger by negation
                if -deny > best_deny:
                    best_deny = -deny

        center_bonus = 0.15 * (base_center - md(nx, ny, cx, cy))  # encourage advancing toward center
        opp_center_pen = 0.05 * (md(nx, ny, ox, oy) - md(sx, sy, ox, oy))
        v = 1.6 * best_gain + 0.7 * (best_deny if best_deny > -10**8 else 0) + center_bonus - opp_center_pen

        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]