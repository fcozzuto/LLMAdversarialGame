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
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        bestv = -10**18
        for rx, ry in resources:
            d1 = cheb(sx, sy, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            gap = d2 - d1
            v = gap * 20 - d1  # prefer resources opponent can't reach first
            if d1 == 0:
                v += 100000
            if gap < 0:
                v -= (abs(gap) * 5 + d1)  # strongly deprioritize
            if v > bestv:
                bestv = v
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    cur_do = cheb(sx, sy, ox, oy)
    bestm = (0, 0)
    bestscore = -10**18
    for dx, dy, nx, ny in legal:
        dn = cheb(nx, ny, tx, ty)
        oppd = cheb(nx, ny, ox, oy)

        score = -dn * 3
        if (nx, ny) == (tx, ty):
            score += 100000

        # Keep some distance if very close to prevent easy contest grabs
        if cur_do <= 2:
            score += (oppd - cur_do) * 6
        else:
            score += (oppd - cur_do) * 2

        # Mild avoidance of stepping into opponent's vicinity
        score -= max(0, 2 - oppd) * 50

        # Prefer moves that don't worsen overall progress too much
        score += (cheb(sx, sy, tx, ty) - dn) * 2

        if score > bestscore:
            bestscore = score
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]