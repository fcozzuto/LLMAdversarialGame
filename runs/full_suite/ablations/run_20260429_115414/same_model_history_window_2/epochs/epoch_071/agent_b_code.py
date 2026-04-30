def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                resources.append((rx, ry))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def neighbor_free_count(x, y):
        c = 0
        for dx, dy in dirs:
            if valid(x + dx, y + dy):
                c += 1
        return c

    if not resources:
        # Fall back: move toward center while staying safe
        cx, cy = w // 2, h // 2
        best = None
        best_val = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            val = -cheb(nx, ny, cx, cy) + 0.1 * neighbor_free_count(nx, ny)
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Heuristic: for each move, pick the resource that maximizes our advantage vs opponent
    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_best = -10**18
        # One-step policy evaluation by scanning resources (deterministic)
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Gain when we are closer than opponent; also slightly prefer tighter space and avoid dead-ends.
            val = (do - ds) * 10 - ds + 0.05 * neighbor_free_count(nx, ny)
            # If we can reach while opponent is far, prioritize sharply.
            if do >= ds + 2:
                val += 50
            my_best = val if val > my_best else my_best
        # Secondary: keep from stepping into worse maneuvering zones
        tie_break = 0.1 * neighbor_free_count(nx, ny) - 0.01 * cheb(nx, ny, ox, oy)
        total = my_best + tie_break
        if total > best_val:
            best_val = total
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]