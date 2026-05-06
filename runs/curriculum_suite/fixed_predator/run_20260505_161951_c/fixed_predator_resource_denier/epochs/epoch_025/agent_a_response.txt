def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacle_set

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            # prefer farther; then prefer staying away from bottom-right corner to reduce symmetry traps
            v = d * 1000 - (abs(nx - (w - 1)) + abs(ny - (h - 1)))
            if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
                bestv = v
                best = [dx, dy]
        return best

    def cell_key(c):
        cx, cy = c
        sd = cheb(cx, cy, x, y)
        od = cheb(cx, cy, ox, oy)
        # primary: maximize advantage (opp further); secondary: closer to own
        return (od - sd, -sd, cx, cy)

    # Deterministic target selection: best advantage, then best locality
    resources_sorted = sorted(resources, key=cell_key, reverse=True)
    target = resources_sorted[0]

    # Try to step toward the target; if multiple moves equally good, prefer ones that also worsen opponent access
    tx, ty = target
    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        # value based on closeness to target and denial: reduce opponent's closeness to that target
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        den = 0
        # If we can move to a cell that increases (or doesn't decrease) opponent-target distance in future, prefer it
        den = cheb(nx, ny, ox, oy) - cheb(x, y, ox, oy)
        v = (opp_d - self_d) * 1000 - self_d * 3 + den
        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]
    return best