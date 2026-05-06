def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

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

    # Choose a resource where we are relatively closer than the opponent (resource denial).
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        self_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        denial = opp_d - self_d  # bigger is better for us
        # tie-breakers: prefer closer resources and then smaller (rx+ry)
        key = (denial, -self_d, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best if best is not None else (w // 2, h // 2)

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        self_d_next = cheb(nx, ny, tx, ty)
        opp_d_next = cheb(nx, ny, ox, oy)

        # Primary: keep/advance denial while reducing distance to target.
        denial_next = opp_d_next - self_d_next
        dist_to_target = self_d_next

        # Secondary: prefer stepping that also reduces our distance to the target (faster capture).
        # Tertiary: keep deterministic tie-breaking with coordinate sum.
        val = (denial_next, -dist_to_target, -(nx + ny))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]