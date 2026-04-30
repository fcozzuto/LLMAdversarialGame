def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not inb(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and cheb(nx, ny, w - 1, h - 1) <= cheb(sx, sy, w - 1, h - 1):
                return [dx, dy]
        return [0, 0]

    center = (w - 1) / 2.0, (h - 1) / 2.0

    # Choose the move that improves our lead over the closest "contested" resource.
    # Lead = (opp_dist - self_dist), prefer larger lead; also prefer nearer self progress.
    best_move = (0, 0)
    best_val = -10**18

    # Deterministic move preference order by fixed iteration.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = 0.0

        # Evaluate top few resources by our current distance to reduce noise.
        # Deterministic: use first k after sorting by distance and then by coordinates.
        ranked = sorted(resources, key=lambda r: (cheb(nx, ny, r[0], r[1]), r[0], r[1]))[:5]
        for rx, ry in ranked:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive means we are closer now
            # Reward strong lead; if tied, pick the resource closer to us.
            v += (lead * 10.0) + (-(ds)) + (0.05 * (cheb(nx, ny, center[0], center[1]) * -1.0))

        # Slight penalty for moving away from resources overall
        current_best_self = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        v += -0.1 * current_best_self

        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]