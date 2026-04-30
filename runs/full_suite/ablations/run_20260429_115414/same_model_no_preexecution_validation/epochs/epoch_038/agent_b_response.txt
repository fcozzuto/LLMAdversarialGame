def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def pick_target():
        if resources:
            best = None
            for rx, ry in resources:
                sd = cheb(sx, sy, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # Prefer resources where we are closer than opponent; then deterministic tie-break
                key = (-(od - sd), -sd, -(rx * 10 + ry))
                if best is None or key > best[0]:
                    best = (key, (rx, ry))
            return best[1]
        return (w - 1 - sx if w > 1 else sx, h - 1 - sy if h > 1 else sy)

    tx, ty = pick_target()

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy  # engine would keep us here; evaluate as staying
        d = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Score: minimize our distance, maximize our relative advantage, deterministic tie-break by direction order
        score = (-d, -(d - od), -cheb(nx, ny, tx, ty), -(dx * 3 + dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]