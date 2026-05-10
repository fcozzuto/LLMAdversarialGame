def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = []
    for p in resources:
        if p and len(p) >= 2:
            res.append((p[0], p[1]))
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

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

    if not res:
        dx = 0
        if ox < sx:
            dx = -1
        elif ox > sx:
            dx = 1
        dy = 0
        if oy < sy:
            dy = -1
        elif oy > sy:
            dy = 1
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
        return [0, 0]

    opp_min = 10**9
    for rx, ry in res:
        d = cheb(ox, oy, rx, ry)
        if d < opp_min:
            opp_min = d

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_min = 10**9
        for rx, ry in res:
            d = cheb(nx, ny, rx, ry)
            if d < my_min:
                my_min = d

        on_resource = 1 if (nx, ny) in res else 0
        # Prefer taking resources immediately; then minimize own nearest distance
        # while keeping opponent's nearest distance larger than ours.
        val = 1000 * on_resource + (opp_min - my_min) * 25 - my_min
        # Small penalty for moving closer to obstacles to reduce being trapped.
        for ax, ay in obs:
            if cheb(nx, ny, ax, ay) == 1:
                val -= 2
                break

        # Deterministic tie-break: prefer staying, then lexicographic dx,dy.
        if val > best_val or (val == best_val and (dx == 0 and dy == 0)):
            best_val = val
            best = [dx, dy]

    if best == [0, 0]:
        # If all moves were invalid, engine will keep us in place anyway.
        return [0, 0]
    return best