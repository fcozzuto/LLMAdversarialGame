def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            resources.append((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obstacles)
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # Choose target with deterministic "advantage" and tie-break by distance.
    tx, ty = ox, oy
    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we're closer/equal
            # Extra: penalize resources that are "farther from escape" near obstacles by discouraging adjacency to obstacles.
            adj = 0
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                ax, ay = rx + dx, ry + dy
                if blocked(ax, ay): adj += 1
            key = (-(adv), ds + adj * 0.1, (rx + 7 * ry) % 97)  # minimize
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]

    # If we are not closer, switch to "intercept": move towards our nearest resource that opponent is likely to contest.
    if resources:
        my_best = (10**9, sx, sy)
        opp_best = (10**9, sx, sy)
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds < my_best[0]: my_best = (ds, rx, ry)
            if do < opp_best[0]: opp_best = (do, rx, ry)
        if my_best[1] == opp_best[1] and my_best[0] > opp_best[0]:
            tx, ty = my_best[1], my_best[2]
        elif my_best[0] > opp_best[0]:
            tx, ty = opp_best[1], opp_best[2]

    # Greedy step towards target with obstacle avoidance; tie-break by also limiting closeness to opponent.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): 
            continue
        ds = cheb(nx, ny, tx, ty)
        d_op = cheb(nx, ny, ox, oy)
        # Prefer getting closer to target, then staying away from opponent, then deterministic tie-break.
        val = (ds, -d_op, (nx * 11 + ny * 3) % 97)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    if best_val is None:
        return [0, 0]
    return [best_move[0], best_move[1]]