def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def risk(x, y):
        r = 0
        for ax in (x - 1, x, x + 1):
            for ay in (y - 1, y, y + 1):
                if (ax, ay) in obstacles:
                    r += 2
        return r

    if not resources:
        # No visible resources: move toward center while keeping distance from opponent
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = -10**9
        for dx, dy, nx, ny in legal:
            v = -md(nx, ny, cx, cy) - 0.25 * md(nx, ny, ox, oy) - 0.5 * risk(nx, ny)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Choose move that maximizes advantage to the best remaining resource
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        best_resource_val = -10**18
        for rx, ry in resources:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            # Higher is better: we prefer resources where we are closer than opponent,
            # also prefer nearer resources in absolute terms.
            val = (do - ds) * 3 - ds - 0.5 * risk(nx, ny) - 0.1 * md(nx, ny, ox, oy)
            if val > best_resource_val:
                best_resource_val = val
        if best_resource_val > best_val:
            best_val = best_resource_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]