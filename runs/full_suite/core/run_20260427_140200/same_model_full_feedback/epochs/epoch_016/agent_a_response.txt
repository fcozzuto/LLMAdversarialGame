def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in dirs if inb(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    if not resources:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dopp = cheb(nx, ny, ox, oy)
            key = (dopp, dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    # Choose a target resource with best "advantage" (self closer than opponent preferred).
    best_t = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Lower is better: prioritize picking when we can reach no later than opponent.
        adv = ds - do
        # Slight tie-break toward nearer resources and toward the center to reduce dithering.
        center = cheb(rx, ry, (w - 1) / 2, (h - 1) / 2)
        key = (adv, ds, center, rx, ry)
        if best_t is None or key < best_t[0]:
            best_t = (key, (rx, ry))

    rx, ry = best_t[1]
    # Move toward chosen target while not letting opponent close in too much.
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds2 = cheb(nx, ny, rx, ry)
        do2 = cheb(ox, oy, rx, ry)
        d_to_opp = cheb(nx, ny, ox, oy)
        # Prefer decreasing distance to target; then keep distance from opponent; deterministic tie-break.
        key = (ds2, -do2, -d_to_opp, dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]]