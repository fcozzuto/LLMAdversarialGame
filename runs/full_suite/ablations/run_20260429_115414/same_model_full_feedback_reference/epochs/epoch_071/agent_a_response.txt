def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def obstacle_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    pen += 2
        return pen

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in moves if inb(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    if not res:
        # deterministic: move away from opponent if possible, else toward center-ish
        best = None
        bestv = -10**9
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, ox, oy) - obstacle_pen(nx, ny)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    def eval_from(x, y):
        # Higher is better: target resources where we are closer than opponent,
        # also slightly prefer safer cells (lower obstacle penalty).
        best_adv = -10**9
        for rx, ry in res:
            myd = cheb(x, y, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # contest-aware advantage; strongly avoid targets opponent is much closer to
            adv = (opd - myd) * 4 - (myd * 0.7) + (opd * 0.1)
            if myd == 0:
                adv += 50
            best_adv = adv if adv > best_adv else best_adv
        return best_adv - obstacle_pen(x, y)

    best = None
    bestv = -10**9
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        v = eval_from(nx, ny)
        # tiny deterministic tie-break: prefer moves that reduce cheb to opponent less (more space)
        if v == bestv:
            if cheb(nx, ny, ox, oy) > cheb(sx + best[0], sy + best[1], ox, oy):
                best = (dx, dy)
        elif v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]