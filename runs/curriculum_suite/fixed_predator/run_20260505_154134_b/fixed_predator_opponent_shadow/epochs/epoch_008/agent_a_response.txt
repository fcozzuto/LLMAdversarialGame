def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    if not resources:
        # Keep distance from opponent if no resources visible
        best = [0, 0]
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Target selection: be decisive about resources where we are (or can become) closer than opponent
    best_t = resources[0]
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        key = (oppd - myd, -myd)  # maximize advantage, then minimize our distance
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t
    myd0 = cheb(sx, sy, rx, ry)
    oppd0 = cheb(sx, sy, ox, oy)

    # Move scoring: advance toward target, while avoiding letting opponent gain (push away from opponent too)
    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, rx, ry)
        oppdist = cheb(nx, ny, ox, oy)
        # Primary: reduce target distance; Secondary: increase separation from opponent
        # Tertiary: if we can't reduce, prefer staying that blocks (higher distance to target)
        v = (myd0 - myd) * 1000 + oppdist - myd * 2
        # Discourage moves that step away from target too much
        if myd > myd0 + 1:
            v -= 500
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best