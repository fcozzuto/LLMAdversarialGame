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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    valid = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if isinstance(rx, int) and isinstance(ry, int) and inb(rx, ry):
                valid.append((rx, ry))
    if not valid:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def best_u(px, py):
        best = -10**18
        for rx, ry in valid:
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # prefer resources we can arrive earlier, then closer
            u = (do - ds) * 45 - ds
            if do > ds:
                u += 250
            # if opponent is not far behind, reduce attraction to contested far targets
            if do <= ds + 1:
                u -= ds * 3
            if u > best:
                best = u
        return best

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy, nx, ny in moves:
        score = best_u(nx, ny)
        # small tie-break: prefer reducing distance to some currently favorable target
        # (deterministic, cheap approximation)
        nearest = 10**9
        for rx, ry in valid:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if do > ds:
                if ds < nearest:
                    nearest = ds
        if nearest == 10**9:
            nearest = cheb(nx, ny, valid[0][0], valid[0][1])
        score += -0.5 * nearest
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move