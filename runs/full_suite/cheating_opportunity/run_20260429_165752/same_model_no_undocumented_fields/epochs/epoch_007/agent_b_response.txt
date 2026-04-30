def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = [(int(r[0]), int(r[1])) for r in observation.get("resources", []) or []]
    obstacles = set((int(o[0]), int(o[1])) for o in observation.get("obstacles", []) or [])
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def safe(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    best = None  # (primary, secondary, dx, dy)
    # If standing on a resource, stay
    if (x, y) in set(resources):
        return [0, 0]

    if resources:
        res_set = set(resources)
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not safe(nx, ny):
                continue
            # Pick move that makes us reach some resource sooner than opponent
            best_r = None
            best_score = None
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer (opponent is farther) then (we are close)
                score = (do - ds, -ds, -cheb(ox, oy, nx, ny), rx, ry)
                if best_score is None or score > best_score:
                    best_score = score
                    best_r = (rx, ry)
            rx, ry = best_r
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Primary: maximize advantage; Secondary: minimize our distance
            primary = -(do - ds)
            secondary = ds
            cand = (primary, secondary, dx, dy)
            if best is None or cand < best:
                best = cand
    if best is not None:
        return [best[2], best[3]]

    # No resources: move toward center while keeping away from opponent
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not safe(nx, ny):
            continue
        to_center = cheb(nx, ny, cx, cy)
        away = cheb(nx, ny, ox, oy)
        # Prefer decreasing center distance and increasing away distance
        cand = (to_center, -away, dx, dy)
        if best is None or cand < best:
            best = cand
    if best is None:
        return [0, 0]
    return [best[2], best[3]]