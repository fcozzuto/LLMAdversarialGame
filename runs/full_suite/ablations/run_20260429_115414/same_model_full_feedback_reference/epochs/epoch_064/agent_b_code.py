def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # go toward opponent to reduce their options
        best = None
        bestv = -10**9
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dopp = cheb(nx, ny, ox, oy)
            val = doppel = -dopp
            if val > bestv:
                bestv = val
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    def nearest_dist(px, py):
        md = 10**9
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if d < md: md = d
        return md

    # assume opponent next move is greedy to their nearest resource
    def opponent_best_after():
        bestd = 10**9
        bestpos = (ox, oy)
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if inb(nx, ny):
                d = nearest_dist(nx, ny)
                if d < bestd:
                    bestd = d
                    bestpos = (nx, ny)
        return bestpos

    opnx, opny = opponent_best_after()
    opp_base = nearest_dist(opnx, opny)

    best_move = legal[0]
    best_score = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        myd = nearest_dist(nx, ny)
        # try to keep ahead: minimize myd and maximize (opp after - my after)
        score = (opp_base - myd) * 10.0
        # slight preference for moving away from opponent if tie on resource pressure
        score += (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy)) * 0.1
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]