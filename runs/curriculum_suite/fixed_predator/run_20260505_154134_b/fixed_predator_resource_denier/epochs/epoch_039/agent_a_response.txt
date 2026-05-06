def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(tuple(p) for p in obstacles)

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

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = [0, 0]
    best_score = None

    if not resources:
        # go toward center as fallback
        tx, ty = w // 2, h // 2
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            score = (-cheb(nx, ny, tx, ty), nx, ny)
            if best_score is None or score > best_score:
                best_score = score
                best = [dx, dy]
        return best

    # evaluate moves by aiming for resources we can contest (we want ds-do small/negative)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        best_contest = None
        best_dist = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            contest = ds - do  # negative means we are closer than opponent to that resource
            if best_contest is None or contest < best_contest or (contest == best_contest and (ds < best_dist)):
                best_contest = contest
                best_dist = ds
        # primary: be ahead on some resource (lower contest), secondary: reduce our distance to that resource
        score = ( -best_contest, -best_dist, -abs((nx - ox)) - abs((ny - oy)), -((nx + ny) % 2), nx, ny )
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best