def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    resources = [(int(x), int(y)) for x, y in (observation.get("resources") or [])]
    obstacles = {(int(x), int(y)) for x, y in (observation.get("obstacles") or [])}

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obs(x, y):
        c = 0
        for ddx, ddy in dirs:
            if (x + ddx, y + ddy) in obstacles:
                c += 1
        return c

    if not resources:
        best = (0, 0)
        bestv = -10**18
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            v = -cheb(nx, ny, cx, cy) - 0.2 * near_obs(nx, ny)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    our_ahead = []
    opp_nearest = None
    opp_nearest_d = 10**9
    for rx, ry in resources:
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        if opp_d < opp_nearest_d:
            opp_nearest_d = opp_d
            opp_nearest = (rx, ry)
        if our_d <= opp_d - 1:
            our_ahead.append((rx, ry, opp_d - our_d, opp_d, our_d))

    if our_ahead:
        target = max(our_ahead, key=lambda t: (t[2], -t[3], -t[4]))[:2]
    else:
        # Try to steal: chase opponent's closest resource, but prefer moves that keep us closer than them.
        target = min(resources, key=lambda r: (cheb(ox, oy, r[0], r[1]), cheb(sx, sy, r[0], r[1])))  # (min opp distance, then ours)

    tx, ty = target
    pn_x, pn_y = opp_nearest

    bestm = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        our_d = cheb(nx, ny, tx, ty)
        opp_d_target = cheb(ox, oy, tx, ty)
        # Interference: penalize helping opponent with their nearest resource.
        opp_d_near = cheb(ox, oy, pn_x, pn_y)
        opp_d_near_after = cheb(ox, oy, pn_x, pn_y)  # opponent position fixed this turn; keep term deterministic but meaningful via relative