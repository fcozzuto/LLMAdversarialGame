def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    best = None
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        self_pos = (nx, ny)

        # Targeting: prefer a resource that we are closer to than opponent,
        # and otherwise chase the opponent's nearest threat.
        self_to = []
        opp_to = []
        for r in resources:
            self_to.append(cheb(self_pos, r))
            opp_to.append(cheb((ox, oy), r))

        # Compute "lead" on best contest target
        lead = -10**9
        nearest_self = 10**9
        nearest_opp = 10**9
        for i, r in enumerate(resources):
            ds = self_to[i]
            do = opp_to[i]
            if ds < nearest_self: nearest_self = ds
            if do < nearest_opp: nearest_opp = do
            # lead positive if we are closer
            l = do - ds
            if l > lead: lead = l

        # If we can land on a resource, strongly prefer it
        on_resource = 1 if self_pos in set(resources) else 0

        # Score combines: immediate pickup, contest lead, and general progress.
        sc = on_resource * 10**6 + lead * 1000 - nearest_self * 5 + nearest_opp * 1

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best