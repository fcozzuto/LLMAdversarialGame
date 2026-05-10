def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1, h - 1) if ((ox + oy) % 2 == 1) else (0, 0)
        bestv, bestm = -10**9, [0, 0]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                v = -cheb(nx, ny, tx, ty) - 0.001 * cheb(nx, ny, ox, oy)
                if v > bestv:
                    bestv, bestm = v, [dx, dy]
        return bestm

    best_score, best_move = -10**18, [0, 0]
    # Deterministic tie-break: prefer earlier deltas order and then smaller dx,dy magnitude.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        best_margin = -10**9
        closer_count = 0
        best_ds = 10**9
        # Compete on all resources; prefer being closer to at least one, and for many.
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds
            if ds < best_ds and margin == best_margin:
                best_ds = ds
            if margin > best_margin:
                best_margin = margin
                best_ds = ds
            if margin > 0:
                closer_count += 1
        # Main objective: maximize contest margin; secondary: maximize number of wins; tertiary: reduce distance.
        score = best_margin * 10.0 + closer_count * 1.5 - 0.05 * best_ds
        if score > best_score:
            best_score, best_move = score, [dx, dy]
    return best_move