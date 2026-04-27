def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    target = None
    best = None
    resources.sort()
    for rx, ry in resources:
        du = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        adv = do - du  # higher is better (we are closer)
        key = (-(adv), du - do, rx + ry, rx, ry)  # deterministic tie-break
        if best is None or key < best:
            best = key
            target = (rx, ry)

    if target is None:
        # No resources known: move to maximize distance from opponent deterministically.
        best_score = None
        best_move = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            score = dist(nx, ny, ox, oy)
            key = (-score, dx, dy)
            if best_score is None or key < best_score:
                best_score = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    tx, ty = target
    best_score = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        du2 = dist(nx, ny, tx, ty)
        do2 = dist(nx, ny, ox, oy)
        # Prefer getting closer to target and, secondarily, increasing our lead over opponent.
        score = (-(du2), do2 - dist(ox, oy, tx, ty), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]