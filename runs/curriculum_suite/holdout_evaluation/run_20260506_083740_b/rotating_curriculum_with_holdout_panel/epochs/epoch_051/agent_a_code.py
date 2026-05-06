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
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    res = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in ob:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def edge_bias(x, y):
        # Edge_patrol: favor denying edge resources and moving toward edges if contesting.
        d0 = min(x, y, w - 1 - x, h - 1 - y)
        return -d0  # closer to edge => larger (less negative) preference

    def best_target_for(posx, posy):
        # Choose resource that maximizes advantage against opponent from current step.
        # If tied, prefer nearer to opponent (more contested) then edge bias then distance from us.
        best = None
        bx, by = None, None
        for rx, ry in res:
            am = md(posx, posy, rx, ry)
            ao = md(ox, oy, rx, ry)
            adv = ao - am  # positive means we are closer
            key = (-(adv), md(ox, oy, rx, ry), -(edge_bias(rx, ry)), am)
            if best is None or key < best:
                best = key
                bx, by = rx, ry
        return bx, by

    tx, ty = best_target_for(sx, sy)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in ob:
            continue
        me_d = md(nx, ny, tx, ty)
        opp_d = md(ox, oy, tx, ty)
        # If we can reduce our distance faster than opponent, value increases.
        value = (opp_d - me_d) * 10 - me_d
        # Add small tie-break: move that also reduces opponent distance to its nearest contested resource.
        ox_best = None
        for rx, ry in res:
            od = md(ox, oy, rx, ry)
            if ox_best is None or od < ox_best:
                ox_best = od
        value += -0.05 * ox_best
        if value > best_val:
            best_val = value
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]