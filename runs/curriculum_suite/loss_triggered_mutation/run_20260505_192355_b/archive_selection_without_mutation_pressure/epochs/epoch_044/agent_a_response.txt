def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # For each candidate move, estimate best contest advantage from the resulting cell.
    best_move = (0, 0)
    best_adv = -10**18
    best_opp_dist = 10**18
    best_self_res_dist = 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Highest advantage over all resources for this next position.
        adv_here = -10**18
        self_res_dist = 10**18
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            d_opp = man(ox, oy, rx, ry)
            d_self = man(nx, ny, rx, ry)
            a = d_opp - d_self
            if a > adv_here:
                adv_here = a
            ds = d_self
            if ds < self_res_dist:
                self_res_dist = ds

        opp_dist = man(nx, ny, ox, oy)

        if (adv_here > best_adv or
            (adv_here == best_adv and opp_dist < best_opp_dist) or
            (adv_here == best_adv and opp_dist == best_opp_dist and self_res_dist < best_self_res_dist)):
            best_adv = adv_here
            best_opp_dist = opp_dist
            best_self_res_dist = self_res_dist
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]