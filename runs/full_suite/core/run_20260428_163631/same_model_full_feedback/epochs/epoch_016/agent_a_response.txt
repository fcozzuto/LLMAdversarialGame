def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            return -10**9
        if (nx, ny) in resources:
            return 10**8  # immediate pickup if present

        # pick target resource with "winnability": prefer where we are not behind opponent
        best = None
        best_val = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Our progress matters; being behind opponent is penalized.
            # Also bias toward resources nearer our side (x small) to diversify deterministically.
            val = (-ds) + 0.6 * (do - ds) - 0.01 * rx + 0.01 * abs(ry - (h // 2))
            if val > best_val:
                best_val = val
                best = (rx, ry, ds, do)

        if best is None:
            # no resources: drift toward center while keeping distance from opponent slightly
            center = (w // 2, h // 2)
            return -cheb(nx, ny, center[0], center[1]) - 0.05 * cheb(nx, ny, ox, oy)

        rx, ry, ds, do = best
        # Additional tactical tweak: reduce chance of giving opponent a "closer-to-target" response
        my_dist_now = cheb(sx, sy, rx, ry)
        opp_dist_now = cheb(ox, oy, rx, ry)
        opp_keeps_edge = 1.0 if do < opp_dist_now else 0.0
        return -ds - 0.15 * max(0, do - ds) - 0.08 * opp_keeps_edge - 0.001 * (abs(rx - nx) + abs(ry - ny))

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        sc = score_move(dx, dy)
        if sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]