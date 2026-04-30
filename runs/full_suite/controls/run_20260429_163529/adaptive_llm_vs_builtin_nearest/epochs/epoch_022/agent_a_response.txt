def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def opp_step(tx, ty, px, py):
        best = (10**9, 10**9, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = px + dx, py + dy
                if not inb(nx, ny) or (nx, ny) in obs:
                    continue
                d = cheb(nx, ny, tx, ty)
                # tie-break deterministically: prefer dx then dy
                key = (d, abs(nx - tx) + abs(ny - ty), dx, dy)
                if key < best:
                    best = key
        return (px + best[2], py + best[3])

    # Choose target giving maximum competitive edge (min myd - opd)
    best_t = None
    best_key = None
    for rx, ry in res:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = (myd - opd, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    # One-step lookahead: evaluate our candidate move with predicted opponent move
    best_move = (10**9, 10**9, 0, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            myd2 = cheb(nx, ny, tx, ty)
            nox, noy = opp_step(tx, ty, ox, oy)
            opd2 = cheb(nox, noy, tx, ty)
            key = (myd2 - opd2, myd2, (nx != tx or ny != ty), dx, dy)
            if key < best_move:
                best_move = key

    return [int(best_move[3]), int(best_move[4])]