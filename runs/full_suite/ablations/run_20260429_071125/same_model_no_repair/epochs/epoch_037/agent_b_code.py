def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obstacle_pen(x, y):
        if (x, y) in occ:
            return -10**18
        pen = 0
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1),(x+1,y+1),(x+1,y-1),(x-1,y+1),(x-1,y-1)):
            if (nx, ny) in occ:
                pen -= 8
        return pen

    if not resources:
        # move toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = -10**18
        bestmv = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            s = -cheb(nx, ny, tx, ty) + obstacle_pen(nx, ny)
            if s > best:
                best = s
                bestmv = (dx, dy)
        return [bestmv[0], bestmv[1]]

    # pick best target resource by how much we can beat opponent to it
    best_lead = -10**18
    target = resources[0]
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        lead = opd - myd  # positive if we are closer
        s = lead * 1000 - myd * 10
        if s > best_lead:
            best_lead = s
            target = (rx, ry)

    rx, ry = target

    best = -10**18
    bestmv = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in occ:
            continue
        myd = cheb(nx, ny, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        lead_after = opd - myd
        # primary: secure closest path; secondary: avoid stepping away if trailing
        s = lead_after * 2000 - myd * 30
        # discourage moving toward opponent if we are already behind on target
        if lead_after < 0:
            s += -cheb(nx, ny, ox, oy) * 2
        # slight general push toward remaining resources
        s += -min(cheb(nx, ny, r[0], r[1]) for r in resources) * 1
        s += obstacle_pen(nx, ny)
        # small tie-break toward reducing distance to opponent-side corner
        s += -cheb(nx, ny, (w - 1 if ox == 0 else 0), (h - 1 if oy == 0 else 0)) * 0.01
        if s > best:
            best = s
            bestmv = (dx, dy)

    return [bestmv[0], bestmv[1]]