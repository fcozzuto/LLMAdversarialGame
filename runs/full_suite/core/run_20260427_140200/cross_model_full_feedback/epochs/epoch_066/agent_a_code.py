def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    if not resources:
        # No resources: maximize distance from opponent deterministically
        bestm = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                v = cheb(nx, ny, ox, oy)
                if v > bestv:
                    bestv = v
                    bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    # Precompute current opponent distances to all resources
    opp_ds = []
    for rx, ry in resources:
        opp_ds.append(cheb(ox, oy, rx, ry))

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)

        # Find best advantage (how much sooner we can reach some resource than opponent)
        best_adv = -10**9
        nearest_res = None
        nearest_d = 10**9
        for i, (rx, ry) in enumerate(resources):
            dm = cheb(nx, ny, rx, ry)
            if dm < nearest_d:
                nearest_d = dm
                nearest_res = (rx, ry)
            adv = opp_ds[i] - dm
            if adv > best_adv:
                best_adv = adv

        # Objective: prioritize taking resources we can reach sooner, while keeping some separation
        val = 4.0 * best_adv - 1.0 * nearest_d + 0.5 * d_opp

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]