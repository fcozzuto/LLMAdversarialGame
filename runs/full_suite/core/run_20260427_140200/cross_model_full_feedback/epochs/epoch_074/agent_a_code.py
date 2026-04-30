def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def closer_target():
        if not resources:
            return None
        best = None
        best_margin = -10**9
        for r in resources:
            dm = cheb((mx, my), r)
            do = cheb((ox, oy), r)
            # if opponent is closer, we prioritize denying it; else we prioritize taking ours
            margin = (do - dm)
            if margin > best_margin:
                best_margin = margin
                best = r
        return best

    target = closer_target()
    if target is None:
        target = (w // 2, h // 2)

    # Deny: if opponent is closer to target, we step to maximize opponent-target distance and minimize our distance.
    opp_closer = cheb((ox, oy), target) <= cheb((mx, my), target)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not inb(nx, ny):
            continue
        d_me = cheb((nx, ny), target)
        d_opp = cheb((ox, oy), target)

        # slight "interference": if we can get adjacent to opponent, prefer it (helps deny contested cells)
        adj_opp = cheb((nx, ny), (ox, oy)) <= 1

        val = 0
        if opp_closer:
            val += 3.0 * (d_opp - d_me)  # prefer getting closer than opponent to shift contest
            val += 0.6 * cheb((nx, ny), (ox, oy))  # keep separation unless adjacent
        else:
            val += 3.0 * (-d_me)  # take target
            val += 0.3 * cheb((nx, ny), (ox, oy))  # avoid getting trapped near opponent

        if adj_opp:
            val += 0.8

        # Obstacle-aware secondary: prefer moves that don't corner us (more legal neighbors)
        deg = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty):
                deg += 1
        val += 0.05 * deg

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]