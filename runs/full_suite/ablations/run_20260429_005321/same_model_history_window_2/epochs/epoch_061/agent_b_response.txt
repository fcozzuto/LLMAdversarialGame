def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obst_risk(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pen += 2 if (dx != 0 and dy != 0) else 1
        return pen

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0, -10**9)

    # Choose a high-value target deterministically from current position:
    # maximize (opponent is farther than us) and also prioritize closer overall.
    target = None
    best_t = -10**9
    for rx, ry in resources:
        dm = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If we are already closer, target becomes stronger; still allow stealing contest.
        t = (do - dm) * 10 - dm * 2 - obst_risk(rx, ry) * 3
        if t > best_t:
            best_t = t
            target = (rx, ry)

    if target is None:
        # No resources visible; just avoid obstacles and drift to center-ish.
        tx, ty = (w // 2), (h // 2)
    else:
        tx, ty = target

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dm = cheb(nx, ny, tx, ty)
        # Also incorporate how much we improve relative to opponent for the same target.
        do = cheb(ox, oy, tx, ty)
        # Bonus for reducing distance; penalty for being near obstacles.
        score = (do - dm) * 12 - dm * 3 - obst_risk(nx, ny) * 4
        # If resources exist, slightly prefer moving toward our closest resource in general.
        if resources:
            best_general = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < best_general:
                    best_general = d
            score -= best_general
        if score > best[2]:
            best = (dx, dy, score)

    dx, dy, _ = best
    return [int(dx), int(dy)]