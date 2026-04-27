def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        target = (tx, ty)
    else:
        target = None
        best = -10**18
        for rx, ry in resources:
            dme = cheb((mx, my), (rx, ry))
            dop = cheb((ox, oy), (rx, ry))
            if dme < dop:
                s = 1000000 - dme
            else:
                s = (dop - dme) - 0.01 * dme
            if s > best:
                best = s
                target = (rx, ry)

    best_move = (0, 0)
    best_u = -10**18
    base_me_opp = cheb((mx, my), (ox, oy))
    t = target
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not legal(nx, ny):
            continue
        dnew = cheb((nx, ny), t)
        u = -dnew
        if (nx, ny) == t:
            u += 200000
        # Encourage reducing opponent pressure (be less reachable/less close)
        opp_dist_change = cheb((nx, ny), (ox, oy)) - base_me_opp
        u += 0.15 * opp_dist_change
        # Slightly prefer moves that reduce distance to target more than diagonal noise
        u += -0.01 * (abs(dx) + abs(dy))
        if u > best_u:
            best_u = u
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]