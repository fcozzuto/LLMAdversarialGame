def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))
        except:
            pass
    if not resources:
        return [0, 0]

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Deterministic strategic change: greedy-step selection with opponent-pressure penalty,
    # also bias toward moving to positions that "own" nearest contested resource.
    best = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # closest resource distance after move
        d_self_min = 10**9
        d_opp_min = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds < d_self_min:
                d_self_min = ds
            if do < d_opp_min:
                d_opp_min = do
        # pick the best contested resource under this move by minimizing (self_dist - opp_dist)
        # and penalize proximity to opponent when it could arrive sooner.
        val = 0
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # want ds small, and ds <= do ideally; if ds > do, heavily penalize
            gap = do - ds  # positive means we are closer
            term = ds * 3 - gap * 5
            if do < ds:
                term += (ds - do) * 20
            # small bias: prefer moving away from opponent when not losing
            if do <= d_opp_min and cheb(nx, ny, ox, oy) <= cheb(sx, sy, ox, oy):
                term += 2
            if term > val:
                val = term
        # primary objective: maximize advantage; secondary: minimize worst-term
        worst_term = val
        advantage = d_opp_min - d_self_min
        if best is None or (advantage > best_val[0]) or (advantage == best_val[0] and worst_term < best_val[1]):
            best = (dx, dy)
            best_val = (advantage, worst_term)

    return [int(best[0]), int(best[1])]