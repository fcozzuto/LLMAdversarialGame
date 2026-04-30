def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a target resource where we are relatively closer than the opponent.
    best = None
    best_val = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = md - 0.85 * od  # lower is better: prioritize resources we can reach sooner
        if best is None or val < best_val or (val == best_val and md < best_val2):
            best = (rx, ry)
            best_val = val
            best_val2 = md

    # If no resources, drift to center deterministically while increasing opponent distance.
    if best is None:
        best = (w // 2, h // 2)

    tx, ty = best
    opp_moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    candidates = []
    for dx, dy in opp_moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(nx, ny, ox, oy)
        # Strongly prefer approaching target; also try to keep opponent far.
        val = ds - 0.6 * do
        # If stepping onto target, value it extremely.
        if (nx, ny) == (tx, ty):
            val -= 100
        candidates.append((val, dx, dy))

    # Deterministic tie-breaker: smallest val then dx then dy.
    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    if candidates:
        return [candidates[0][1], candidates[0][2]]
    return [0, 0]