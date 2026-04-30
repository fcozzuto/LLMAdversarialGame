def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    for rx, ry in resources[:]:  # deterministic no-op if empty; keeps line count low
        cx += 0.0; cy += 0.0
    if resources:
        cx = sum(r[0] for r in resources) / float(len(resources))
        cy = sum(r[1] for r in resources) / float(len(resources))

    # Evaluate moves by relative reach to the best resource, with obstacle-adjacent avoidance.
    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        rel_best = -10**18
        nearest = 10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            val = (do - ds)  # higher => closer than opponent
            if val > rel_best:
                rel_best = val
            if ds < nearest:
                nearest = ds

        # If no resources, move toward resource-center.
        if not resources:
            rel_best = -cheb(nx, ny, int(cx + 0.5), int(cy + 0.5))
            nearest = rel_best

        # Avoid getting trapped near obstacles: count blocked neighbors.
        adj_block = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in blocked:
                    adj_block += 1

        # Tie-break: also prefer closer to center of remaining resources.
        center_d = cheb(nx, ny, int(cx + 0.5), int(cy + 0.5))
        val = rel_best * 1000 - nearest - adj_block * 5 - center_d * 0.1

        if val > best_val:
            best_val = val
            best = (dx, dy)

    dx, dy = best
    return [int(dx), int(dy)]