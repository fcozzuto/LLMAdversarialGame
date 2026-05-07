def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not inb(sx, sy):
        return [0, 0]

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if resources:
        best_key = None
        best_move = (0, 0)
        for dx, dy, nx, ny in valid:
            # Choose a resource where we gain/maintain earliest arrival vs opponent.
            best_for_move = None
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Primary: advantage in earliest arrival after our move.
                # Tie-breaks: prefer shorter ds, then closer to center to reduce dithering.
                adv = do - ds
                center = cheb(nx, ny, w // 2, h // 2)
                k = (adv, -ds, -center, rx, ry)
                if best_for_move is None or k > best_for_move:
                    best_for_move = k
            if best_key is None or best_for_move > best_key:
                best_key = best_for_move
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No visible resources: move toward the farthest corner from opponent (denial-style positioning).
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    best = None
    best_k = None
    for dx, dy, nx, ny in valid:
        k = (-cheb(nx, ny, tx, ty), -cheb(nx, ny, ox, oy))
        if best_k is None or k > best_k:
            best_k = k
            best = (dx, dy)
    return [best[0], best[1]]