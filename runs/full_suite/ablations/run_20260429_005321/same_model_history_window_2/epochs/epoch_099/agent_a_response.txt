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
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # move to increase distance from opponent while staying legal
        best = [0, 0]
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # pick target resource with maximal (opponent_dist - my_dist), tie-break by nearest to me then lexicographic
    best_res = None
    best_adv = -10**18
    best_my = 10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        adv = oppd - myd
        if adv > best_adv or (adv == best_adv and (myd < best_my or (myd == best_my and (rx, ry) < best_res))):
            best_adv = adv
            best_my = myd
            best_res = (rx, ry)

    rx, ry = best_res
    # choose move that maximizes (advantage after move), with safety fallback to any move
    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd = cheb(nx, ny, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        v = (oppd - myd)
        # tiny deterministic preference to reduce distance to chosen resource
        v2 = v * 1000 - myd
        if v2 > bestv:
            bestv = v2
            best = [dx, dy]
    return best