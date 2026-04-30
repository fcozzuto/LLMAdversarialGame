def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Candidate "intercept" resources: those closer to us than opponent, but also those opponent wants.
    best_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Score by our ability to secure a resource and deny opponent.
        best = -10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Favor resources we can reach now; if not, deny by maximizing opponent's remaining distance.
            if ds <= do:
                val = 120 - 4 * ds + 2 * (do - ds)
            else:
                val = -3 * ds + 3 * (do - ds) - 2
            # Small preference toward reducing absolute distance to any resource (keeping tempo).
            val += -0.25 * min(cheb(nx, ny, rr[0], rr[1]) for rr in resources if tuple(rr) not in obstacles)
            # Avoid being too close to opponent unless we can secure.
            if do <= ds:
                val -= 10
            best = val if val > best else best
        # Center/optionality boost to change policy after poor epoch.
        cx, cy = w // 2, h // 2
        best += -0.5 * cheb(nx, ny, cx, cy)
        best_moves.append((best, dx, dy))

    if not best_moves:
        return [0, 0]
    best_moves.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(best_moves[0][1]), int(best_moves[0][2])]