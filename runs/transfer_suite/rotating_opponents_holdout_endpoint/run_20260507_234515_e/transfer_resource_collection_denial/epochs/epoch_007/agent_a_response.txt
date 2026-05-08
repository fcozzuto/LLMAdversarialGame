def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set((p[0], p[1]) for p in obs_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def is_safe(x, y):
        return inside(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Choose best target resource by "we are closer than opponent"
    best_r = resources[0]
    best_ts = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd
        # Slight bias toward moving in general toward the resource (smaller sd)
        ts = lead * 1000000 - sd
        if best_ts is None or ts > best_ts:
            best_ts = ts
            best_r = (rx, ry)

    rx, ry = best_r

    # Move selection: maximize our lead after move; avoid obstacles strongly
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic preference: reduce distance to target, then minimize steps toward increasing x,y
    scored = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        safe = (nx, ny) not in obstacles
        if not safe and (dx, dy) != (0, 0):
            # Strongly discourage but still allow if no other safe moves exist (handled later)
            penalty = 10**12
        else:
            penalty = 0

        sd2 = cheb(nx, ny, rx, ry)
        od2 = cheb(ox, oy, rx, ry)  # opponent position unchanged this turn
        lead2 = od2 - sd2
        # Prefer shorter remaining distance; mild bias to direction toward target (deterministic)
        dir_bonus = -(abs(nx - rx) + abs(ny - ry))
        ts = lead2 * 1000000 - sd2 + dir_bonus - penalty
        scored.append((ts, safe, dx, dy))

    # If every non-stay move is blocked, allow stay as last resort; otherwise pick best safe
    scored.sort(key=lambda t: (t[1], t[0], -t[2], -t[3], t[2], t[3]), reverse=True)
    if scored and not any(t[1] for t in scored):
        return [0, 0]
    for ts, safe, dx, dy in scored:
        if safe:
            return [dx, dy]
    return [0, 0]