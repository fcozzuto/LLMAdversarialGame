def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obs_list = observation.get('obstacles', []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx if dx >= 0 else -dx if dy == 0 else (dy if dy >= 0 else -dy) if dx == 0 else (dx if dx >= 0 else -dx) if (dx if dx >= 0 else -dx) >= (dy if dy >= 0 else -dy) else (dy if dy >= 0 else -dy)

    # Fix cheb implementation bug above by using simpler max(abs()) deterministically
    def cheb(a, b):
        ax, ay = a
        bx, by = b
        da = ax - bx
        if da < 0:
            da = -da
        db = ay - by
        if db < 0:
            db = -db
        return da if da >= db else db

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    next_positions = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            next_positions.append((dx, dy, nx, ny))

    # If all blocked (rare), allow staying
    if not next_positions:
        return [0, 0]

    # Deterministic tie-break: prefer moves that reduce self->opponent distance when utilities tie
    def utility(nx, ny):
        if resources:
            d_s = None
            d_o = None
            best_ds = 10**9
            best_do = 10**9
            # Also consider a "deny" objective when opponent is closer to a resource
            deny_strength = -10**9
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                ds = cheb((nx, ny), (rx, ry))
                do = cheb((ox, oy), (rx, ry))
                if ds < best_ds:
                    best_ds = ds
                    d_s = rx, ry
                if do < best_do:
                    best_do = do
                    d_o = rx, ry
                # Deny objective: maximize (opponent_closer_than_us) at some resource
                deny_strength = max(deny_strength, (do - ds))
            # Main: maximize (opp_d - self_d) to nearest contested resource; also move toward our nearest.
            val = 12 * (best_do - best_ds) - 2 * best_ds + deny_strength
            return val
        # No resources: move to deny by approaching opponent but not colliding with obstacles
        ds_to_opp = cheb((nx, ny), (ox, oy))
        return -ds_to_opp

    best = None
    for dx, dy, nx, ny in next_positions:
        u = utility(nx, ny)
        tie = cheb((nx, ny), (ox, oy))  # smaller is better
        key = (u, -tie)  # maximize u, then minimize distance to opponent
        if best is None or key > best[0]:
            best = (key, [dx, dy])
    return best[1]