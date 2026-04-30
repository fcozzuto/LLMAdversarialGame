def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cell_block_score(nx, ny, tx, ty):
        # discourage stepping into the "opponent-approach" line to target when too close
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        if opd <= myd:
            # add penalty if opponent is already nearer to this cell's direction
            return -2 * (opd - myd)
        return 0

    best_t = None
    best_s = -10**18
    # Target selection: contest resources where opponent is closer, otherwise take ones we can "deny" (opponent farther)
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        if opd == myd and myd > 0:
            # slight bias to closer-to-center path to break ties deterministically
            cx, cy = w // 2, h // 2
            center_bias = cheb(rx, ry, cx, cy) * 0.1
        else:
            center_bias = 0
        # prioritize contesting opponent-leaning targets: (myd - opd) small
        contest = -max(0, opd - myd) * 5 + min(0, myd - opd) * 2
        deny = (opd - myd) * 4
        s = deny + contest - myd - center_bias
        # if opponent is much closer, increase urgency to contest
        if opd + 1 < myd:
            s += 6
        if s > best_s:
            best_s = s
            best_t = (rx, ry)

    if best_t is None:
        # fallback: go toward opponent's corner to force interaction
        tx, ty = 0, 0
    else:
        tx, ty = best_t

    cxands = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # also discourage letting opponent potentially grab the same target
            score = -myd * 3 + (opd - myd) * 2 + cell_block_score(nx, ny, tx, ty)
            cxands.append((score, dx, dy, nx, ny))
    if not cxands: