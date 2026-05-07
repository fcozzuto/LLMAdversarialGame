def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not valid(nx, ny):
            continue

        local_best = -10**18
        picked = False
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if nx == rx and ny == ry:
                picked = True
                local_best = 10**9
                break
            # Prefer states where we are closer than opponent; strongly prefer leads.
            v = (od - sd) * 20 - sd
            if v > local_best:
                local_best = v

        if local_best < -10**17:
            continue

        # Risk: if opponent is very close to taking your best target sooner, avoid.
        risk = 0
        if not picked:
            # Approximate with closest resource to opponent.
            opp_closest = 10**9
            for rx, ry in resources:
                d = man(ox, oy, rx, ry)
                if d < opp_closest:
                    opp_closest = d
            # Penalize if you are also far (likely give up initiative).
            my_closest = 10**9
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if d < my_closest:
                    my_closest = d
            if opp_closest <= 1:
                risk -= 80
            else:
                risk -= (my_closest - opp_closest) * 2

        # Small tie-break: prefer moving closer to currently best-leading resource.
        tie = -man(nx, ny, ox, oy)

        val = local_best + risk + tie
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]