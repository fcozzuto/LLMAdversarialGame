def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Select target resource to race for: maximize opponent advantage; break ties toward nearer/safer resources.
    best = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        win = oppd - myd
        # Prefer resources farther from obstacles (simple local safety).
        near_obs = 0
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            if (rx+dx, ry+dy) in obs:
                near_obs += 1
        center = cheb(rx, ry, w // 2, h // 2)
        key = (win, -myd, -near_obs, -center, -(rx * 9 + ry))
        if best is None or key > best[0]:
            best = (key, rx, ry)
    if best is None:
        return [0, 0]
    _, tx, ty = best

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    bestm = None
    myd0 = cheb(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        # Primary: reduce distance to target; Secondary: keep/extend race lead; Tertiary: avoid getting too close to opponent.
        gain = (myd0 - myd)
        race = oppd - myd
        close_opp = cheb(nx, ny, ox, oy)
        key = (gain, race, -close_opp, -(nx * 9 + ny))
        if bestm is None or key > bestm[0]:
            bestm = (key, dx, dy)

    if bestm is None:
        return [0, 0]
    return [bestm[1], bestm[2]]