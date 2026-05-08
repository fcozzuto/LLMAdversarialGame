def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y) and (x != sx or y != sy):
                res.append((x, y))

    if not res:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        if ox > sx:
            tx = max(0, tx - 1)
        if oy > sy:
            ty = max(0, ty - 1)
        tx = min(w - 1, max(0, tx))
        ty = min(h - 1, max(0, ty))
        res = [(tx, ty)]

    best = None
    best_score = -10**18
    for x, y in res:
        ds = cheb(x, y, sx, sy)
        do = cheb(x, y, ox, oy)
        # Prefer resources where we are closer; penalize being behind.
        score = (do - ds) * 3 - ds
        # Slightly favor progress toward opponent-front (helps race & denies).
        score += (x - sx) * 0.05 + (y - sy) * 0.05
        # Avoid targets too close to opponent if we are not winning the race.
        if do <= ds:
            score -= 2
        if score > best_score:
            best_score = score
            best = (x, y)

    tx, ty = best
    dx = 0
    dy = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    # Try diagonal first, then orthogonal, then stay, with deterministic tie-break.
    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    for cdx, cdy in candidates:
        nx, ny = sx + cdx, sy + cdy
        if valid(nx, ny):
            return [cdx, cdy]

    return [0, 0]