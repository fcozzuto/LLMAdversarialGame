def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles", []) or []))

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

    def obs_prox(x, y):
        if not obstacles:
            return 10
        best = 10
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
                if best == 0:
                    return 0
        return best

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    if resources:
        best = None
        best_score = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we are farther, deprioritize; otherwise race for the best advantage.
            score = (do - ds) * 10
            score += (obs_prox(sx, sy) - obs_prox(rx, ry))
            score += -0.01 * (rx + ry)  # deterministic tie-break
            if score > best_score:
                best_score = score
                best = (rx, ry)
        tx, ty = best
    else:
        # No resources: try to establish mid-control while staying safer from obstacles.
        tx, ty = (w - 1) // 2, (h - 1) // 2
        if cheb(sx, sy, tx, ty) == cheb(ox, oy, tx, ty):
            tx, ty = (w - 1) // 2 + (-1 if sx > ox else 1), (h - 1) // 2

    best_move = (0, 0)
    best_val = -10**18
    base_do = cheb(ox, oy, tx, ty)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        new_ds = cheb(nx, ny, tx, ty)
        # Primary: maximize relative advantage against opponent for this target.
        rel = base_do - new_ds
        # Secondary: avoid obstacles and prefer progress toward target.
        safe = obs_prox(nx, ny)
        progress = cheb(sx, sy, tx, ty) - new_ds
        val = rel * 100 + safe * 2 + progress * 0.5
        # Tertiary deterministic tie-break
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]