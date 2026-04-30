def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_for(x, y):
        if resources:
            d = 10**9
            tx, ty = resources[0]
            for rx, ry in resources:
                dd = cheb(x, y, rx, ry)
                if dd < d:
                    d = dd
                    tx, ty = rx, ry
            # Prefer getting closer; tie-break deterministically by target position and staying still
            return (-d, tx, ty, 0 if (x == sx and y == sy) else 1)
        # No resources: head toward center
        cx, cy = (w - 1) // 2, (h - 1) // 2
        d = cheb(x, y, cx, cy)
        return (-d, x, y, 0 if (x == sx and y == sy) else 1)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            candidates.append((best_for(nx, ny), dx, dy))

    if not candidates:
        # If somehow stuck (shouldn't happen), return a deterministic in-bounds step if possible
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                return [dx, dy]
        return [0, 0]

    candidates.sort()
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]