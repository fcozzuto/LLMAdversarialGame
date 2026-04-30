def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Move evaluation: after one step, choose position that maximizes our "lead"
    # where lead = opponent_closest_to_resources - our_closest_to_resources,
    # and slightly favors moving into good resource zones.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            v = -d
            if v > bestv:
                bestv = v
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    res_list = resources
    opp_base = None
    # compute opponent closest to any resource (constant across our moves)
    opp_best = 10**9
    opp_second = 10**9
    for rx, ry in res_list:
        d = cheb(ox, oy, rx, ry)
        if d < opp_best:
            opp_second = opp_best
            opp_best = d
        elif d < opp_second:
            opp_second = d
    opp_base = opp_best

    best = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        self_best = 10**9
        self_second = 10**9
        min_reachable = 10**9
        deny_value = 0

        for rx, ry in res_list:
            ds = cheb(nx, ny, rx, ry)
            if ds < self_best:
                self_second = self_best
                self_best = ds
            elif ds < self_second:
                self_second = ds

            # Deny: resources where opponent is not as close as we become
            do = cheb(ox, oy, rx, ry)
            # if we are closer (or tie) then it weakens opponent's chance
            if ds <= do:
                # prefer closer/tighter opportunities; also prefer reducing opponent best distance
                deny_value += (do - ds) + (2 if ds == self_best else 0)

            if ds < min_reachable:
                min_reachable = ds

        # Main objective: maximize (opp_closest - self_closest)
        lead = opp_base - self_best
        # Secondary: favor having a "tight" second option (more flexibility) and bigger deny_value
        flex = 0 if self_second >= 10**9 else (self_second - self_best)