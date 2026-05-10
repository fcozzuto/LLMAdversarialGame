def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_list:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    res = []
    for r in resources:
        if r is None or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))

    if not res:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        our_best = 10**9
        opp_best = 10**9
        # pick resource that maximizes our advantage after this move
        best_adv = -10**9
        for rx, ry in res:
            d_ours = cheb((nx, ny), (rx, ry))
            d_opp = cheb((ox, oy), (rx, ry))
            # higher advantage is better; break ties toward closer win
            adv = (d_opp - d_ours)  # positive means we arrive earlier
            if adv > best_adv:
                best_adv = adv
                our_best = d_ours
                opp_best = d_opp
            elif adv == best_adv:
                if d_ours < our_best:
                    our_best = d_ours
                    opp_best = d_opp
        # anti-stalling: prefer reducing our distance to the best resource
        cand.append((best_adv, -our_best, opp_best, dx, dy))

    # If all moves invalid, stay
    if not cand:
        return [0, 0]

    cand.sort(reverse=True, key=lambda t: (t[0], t[1], -t[2], -t[3], -t[4]))
    return [int(cand[0][3]), int(cand[0][4])]