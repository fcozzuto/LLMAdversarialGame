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

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_dxdy = (0, 0)
    best_val = -10**18
    res_list = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                res_list.append((rx, ry))
    if not res_list:
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0

        center_bias = -(abs(nx - cx) + abs(ny - cy))
        # pick the best "deny" target: maximize (opp_dist - my_dist)
        best_adv = -10**9
        best_my_dist = 10**9
        best_opp_dist = 10**9
        for rx, ry in res_list:
            dm_me = man(nx, ny, rx, ry)
            dm_opp = man(ox, oy, rx, ry)
            adv = dm_opp - dm_me
            if adv > best_adv or (adv == best_adv and (dm_me < best_my_dist or (dm_me == best_my_dist and dm_opp < best_opp_dist))):
                best_adv, best_my_dist, best_opp_dist = adv, dm_me, dm_opp

        # if opponent is extremely close to some resource, reduce value unless we also improve the advantage
        opp_pressure = 0
        if best_opp_dist <= 2 and best_adv < 1:
            opp_pressure = -5

        # avoid walking adjacent to opponent when we have no advantage (helps against edge_patrol trapping)
        adj_opp = (abs(nx - ox) <= 1 and abs(ny - oy) <= 1 and (nx != ox or ny != oy))
        trap_pen = -3 if adj_opp and best_adv <= 0 else 0

        val = best_adv * 100 - best_my_dist + center_bias + opp_pressure + trap_pen
        if val > best_val:
            best_val = val
            best_dxdy = (dx, dy)
        elif val == best_val:
            # deterministic tie-break: prefer moves with smaller dx, then dy, then non-staying
            if (dx, dy) < best_dxdy:
                best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]