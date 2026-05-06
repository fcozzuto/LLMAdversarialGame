def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty) - 0.2 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Evaluate moves: win by taking resources sooner and denying opponent routes near them.
    bestv = -10**18
    best = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Resource race: compare our progress to opponent on the best "contested" resource.
        best_race = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Strongly prefer resources where we're closer or about to arrive first.
            race = (do - ds) * 100 - ds
            # If we're already at it (or adjacent), big reward.
            if ds == 0:
                race += 500
            elif ds == 1:
                race += 100
            best_race = race if race > best_race else best_race

        # Safety: if opponent can quickly reach us, avoid.
        d_opp = cheb(nx, ny, ox, oy)
        safety = d_opp * 5

        # Encourage not drifting into walls/obstacles: penalize moves with many blocked neighbors.
        blocked = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax2, ay2 = nx + adx, ny + ady
                if not inb(ax2, ay2) or (ax2, ay2) in obstacles:
                    blocked += 1
        wall_pen = blocked * 0.5

        v = best_race + safety - wall_pen
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best