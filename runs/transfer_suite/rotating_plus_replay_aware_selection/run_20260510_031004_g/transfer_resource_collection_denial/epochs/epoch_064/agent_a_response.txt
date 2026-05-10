def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    my_best = None
    my_key = None
    opp_best = None
    opp_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = (do - ds) * 1000 - ds
        key1 = (adv, -ds, -rx, -ry)
        if my_key is None or key1 > my_key:
            my_key = key1
            my_best = (rx, ry)

        key2 = (-do, ds, -rx, -ry)  # closest to opponent; tie favors longer for us to deter less? (via ds)
        if opp_key is None or key2 > opp_key:
            opp_key = key2
            opp_best = (rx, ry)

    # If opponent is materially closer than we are, contest their closest target; otherwise go for our advantage.
    rx1, ry1 = my_best
    ds1 = cheb(sx, sy, rx1, ry1)
    do1 = cheb(ox, oy, rx1, ry1)

    rx2, ry2 = opp_best
    ds2 = cheb(sx, sy, rx2, ry2)
    do2 = cheb(ox, oy, rx2, ry2)

    if do2 + 1 < ds2 and do2 + 2 <= ds1:
        tx, ty = rx2, ry2
    else:
        tx, ty = rx1, ry1

    dx = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    dy = 0
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    return [dx, dy]