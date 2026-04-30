def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            resources.append((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Deterministic tie-breaker order pref: toward lower dx, then lower dy (consistent with dirs order)
    for dx, dy in dirs:
        nx, ny = int(sx + dx), int(sy + dy)
        if blocked(nx, ny):
            continue

        # If no resources, move to reduce distance to opponent baseline corner
        if not resources:
            val = -cheb(nx, ny, ox, oy)
        else:
            # Choose move that maximizes advantage for the best target resource
            val = -10**18
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer resources where we are closer than opponent; also prefer nearer ones
                gap = (do - ds)
                candidate = gap * 20 - ds  # strong pressure to win targets
                if candidate > val:
                    val = candidate

            # Mild anti-stall: encourage moves that decrease distance to our current best target
            # (computed against the globally best target from current position)
            cur_best = None
            cur_best_val = -10**18
            for rx, ry in resources:
                ds0 = cheb(sx, sy, rx, ry)
                do = cheb(ox, oy, rx, ry)
                gap0 = (do - ds0)
                c0 = gap0 * 20 - ds0
                if c0 > cur_best_val:
                    cur_best_val = c0
                    cur_best = (rx, ry)
            if cur_best is not None:
                ds_cur = cheb(sx, sy, cur_best[0], cur_best[1])
                ds_new = cheb(nx, ny, cur_best[0], cur_best[1])
                val += (ds_cur - ds_new) * 2

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]