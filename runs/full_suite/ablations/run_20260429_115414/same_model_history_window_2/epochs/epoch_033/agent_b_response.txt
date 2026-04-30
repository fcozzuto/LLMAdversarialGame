def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # deterministic "orbit" move away from opponent a bit
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            d = cheb(nx, ny, ox, oy)
            key = (d, -dx, -dy)
            if best is None or key > best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    best_key = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # choose our closest target from this candidate
        our_best_d = 10**9
        our_target = resources[0]
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < our_best_d:
                our_best_d = d
                our_target = (rx, ry)

        rx, ry = our_target
        opp_d = cheb(ox, oy, rx, ry)

        # maximize capture advantage; strongly prefer stepping onto a resource
        capture = 1 if (nx, ny) == (rx, ry) else 0
        obj = (opp_d - our_best_d)
        obj += 1000 * capture

        # small secondary: prefer increasing distance from opponent when advantage ties
        opp_dist = cheb(nx, ny, ox, oy)
        key = (obj, opp_dist, -our_best_d, -dx, -dy, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move