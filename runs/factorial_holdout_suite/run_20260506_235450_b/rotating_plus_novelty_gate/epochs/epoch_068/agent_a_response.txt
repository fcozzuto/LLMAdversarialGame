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
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs or not inb(x, y)

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

    best = None
    best_key = -10**18
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not (isinstance(rx, int) and isinstance(ry, int)):
            continue
        if blocked(rx, ry):
            continue
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer; otherwise maximize our lead gain.
        key = (dO - dS) * 100 - dS
        if dS <= dO:
            key += 500
        if key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    rx, ry = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_move_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        dSn = cheb(nx, ny, rx, ry)
        dOn = cheb(ox, oy, rx, ry)  # opponent stationary this turn; deterministic tie-break below
        # Move that gets us to target faster, and if tied, keeps opponent farther from the target.
        val = -dSn * 10 - dOn
        # Secondary: avoid moving away from our target.
        if dSn <= cheb(sx, sy, rx, ry):
            val += 3
        if val > best_move_val:
            best_move_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]