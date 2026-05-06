def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        dx = dx if dx >= 0 else -dx
        dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    tx0, ty0 = w // 2, h // 2

    def choose_target(px, py):
        if not resources:
            return (tx0, ty0)
        best_pref = None
        best_other = None
        for rx, ry in resources:
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds <= do:
                # prefer resources we can reach no later than opponent, then maximize advantage
                key = (do - ds, -ds, -cheb(px, py, tx0, ty0), rx, ry)
                if best_pref is None or key > best_pref:
                    best_pref = key
            else:
                # contested: minimize how much faster opponent is, then closest for us
                gap = do - ds
                key = (-gap, -ds, rx, ry)
                if best_other is None or key > best_other:
                    best_other = key
        if best_pref is not None:
            return (best_pref[3], best_pref[4])
        if best_other is not None:
            return (best_other[2], best_other[3])
        return resources[0]

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -cheb(nx, ny, tx0, ty0)
            if best is None or v > best[0]:
                best = (v, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        target = choose_target(nx, ny)
        rx, ry = target
        ds = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # primary: keep opponent farther from the target than we are; secondary: closer to target; tertiary: slightly away from opponent to reduce denial radius
        score = (do - ds, -ds, cheb(nx, ny, ox, oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]