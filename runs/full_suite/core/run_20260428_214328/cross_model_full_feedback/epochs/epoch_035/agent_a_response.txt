def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in (observation.get("resources", []) or []):
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst and (nx, ny) != (ox, oy):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not res:
        # Maximize distance from opponent deterministically
        best = None
        bestv = None
        for dx, dy, nx, ny in legal:
            v = cheb(nx, ny, ox, oy)
            if bestv is None or v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Choose candidate targets: nearest to self and nearest to opponent (up to 2 distinct)
    ds = [(cheb(sx, sy, rx, ry), i) for i, (rx, ry) in enumerate(res)]
    do = [(cheb(ox, oy, rx, ry), i) for i, (rx, ry) in enumerate(res)]
    ds.sort(); do.sort()
    cand_idx = []
    for _, i in (ds + do):
        if i not in cand_idx:
            cand_idx.append(i)
        if len(cand_idx) >= 2:
            break
    if not cand_idx:
        cand_idx = [0]

    # Score move by best achievable relative advantage over chosen targets
    best = None
    bestv = None
    for dx, dy, nx, ny in legal:
        cur = 0
        # Encourage staying/heading to resources while preventing easy opponent advantage
        for idx in cand_idx:
            rx, ry = res[idx]
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # If we are on/near resource, prioritize; otherwise maximize margin (opponent further)
            margin = opd - myd
            v = margin * 10
            if (nx, ny) == (rx, ry):
                v += 1000
            # Small penalty if moving closer to opponent overall (deterministic shaping)
            v -= cheb(nx, ny, ox, oy)
            # Tie-break with slight preference toward smaller my distance
            v -= myd * 0.1
            if v > cur:
                cur = v
        if bestv is None or cur > bestv:
            bestv = cur; best = (dx, dy)
    return [best[0], best[1]]