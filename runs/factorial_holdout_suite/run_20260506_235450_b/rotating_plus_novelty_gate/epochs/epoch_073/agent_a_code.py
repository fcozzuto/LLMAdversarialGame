def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def blocked(x, y):
        return (x, y) in obs or not (0 <= x < w and 0 <= y < h)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def move_to(tx, ty):
        best = [0, 0]
        best_v = -10**18
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if blocked(nx, ny):
                    continue
                v = -(cheb(nx, ny, tx, ty))  # maximize closeness to target
                if (nx, ny) in resources_set:
                    v += 5  # strong bias to step onto visible resources
                if dx == 0 and dy == 0:
                    v -= 0.2
                if v > best_v:
                    best_v = v
                    best = [dx, dy]
        return best

    resources_set = set()
    valid_resources = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if isinstance(rx, int) and isinstance(ry, int) and 0 <= rx < w and 0 <= ry < h and not blocked(rx, ry):
                resources_set.add((rx, ry))
                valid_resources.append((rx, ry))
    if not valid_resources:
        return [0, 0]

    # Strategic change: avoid resources where opponent is not meaningfully slower; prioritize safe "contested-losing" wins.
    best_r = valid_resources[0]
    best_score = -10**18
    for rx, ry in valid_resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive means we are closer or can arrive first
        # Penalize equal/losing contests; reward clear lead; secondary: shorter time for tie-break.
        score = lead * 100 - ds * 2
        if lead <= 0:
            score -= (1 - lead) * 50
        # Micro-bias: slightly prefer resources that also reduce opponent's ability next turn
        score += max(0, (ds - do)) * -5
        if score > best_score:
            best_score = score
            best_r = (rx, ry)

    tx, ty = best_r
    return move_to(tx, ty)