def choose_move(observation):
    w = observation.get("grid_width")
    h = observation.get("grid_height")
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", [])
    obs = set(obstacles)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not w or not h:
        return [0, 0]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = observation.get("resources", [])
    if resources:
        tx, ty = min(resources, key=lambda r: (cheb(ox, oy, r[0], r[1]), r[0], r[1]))
    else:
        tx, ty = ox, oy

    best = None
    bestd = 10**9
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        # Prefer moves that reduce distance to target, tie-break deterministically
        d = cheb(nx, ny, tx, ty)
        if d < bestd or (d == bestd and (dx, dy) < best):
            bestd = d
            best = (dx, dy)

    if best is None:
        # try staying put if valid
        if valid(x, y):
            return [0, 0]
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]