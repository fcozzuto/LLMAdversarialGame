def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

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

    # Pick a target resource where we are (or become) advantaged in reachability.
    def best_resource():
        best = None
        best_key = None
        for cx, cy in resources:
            sd = cheb(sx, sy, cx, cy)
            od = cheb(ox, oy, cx, cy)
            # Prefer: maximize (od - sd). If tie, minimize sd, then deterministic coords.
            key = (od - sd, -sd, -cx, -cy)
            if best_key is None or key > best_key:
                best_key = key
                best = (cx, cy)
        return best

    target = best_resource()
    if target is None:
        return [0, 0]
    tx, ty = target

    # Move: avoid obstacles; maximize advantage improvement and progress to target.
    candidates = []
    for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        sd_now = cheb(sx, sy, tx, ty)
        sd_new = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Primary: increase advantage margin to target (od - sd_new).
        # Secondary: decrease sd_new (closer).
        # Tertiary: deterministic tie by coordinate.
        key = (od - sd_new, -sd_new, -(nx + 17 * ny), -dx, -dy)
        candidates.append((key, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]