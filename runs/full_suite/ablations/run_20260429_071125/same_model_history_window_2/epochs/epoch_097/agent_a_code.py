def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs.sort(key=lambda d: (d[0], d[1]))

    if not resources:
        # Fallback: drift toward center while respecting obstacles
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -(abs(nx - cx) + abs(ny - cy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # New policy: maximize "capture swing" against the opponent for a contested resource
    # Score: our distance advantage after the move, with a small bonus for being closer to center-line of resources.
    best_move = (0, 0)
    best_val = -10**18
    # Precompute resource center-ish for tie-breaking
    rx_avg = sum(x for x, y in resources) / float(len(resources))
    ry_avg = sum(y for x, y in resources) / float(len(resources))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = -10**18
        for tx, ty in resources:
            dself = cheb(nx, ny, tx, ty)
            dopp = cheb(ox, oy, tx, ty)
            # big reward if we can reach first (or equal), otherwise push to deny by reducing our distance more
            swing = (dopp - dself)
            # slight preference toward resources that are "globally relevant"
            center_bias = -0.05 * cheb(nx, ny, int(rx_avg), int(ry_avg))
            # if we can pick up immediately, dominate
            immediate = 2.0 if dself == 0 else 0.0
            cand = immediate + swing + center_bias
            if cand > val:
                val = cand
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]