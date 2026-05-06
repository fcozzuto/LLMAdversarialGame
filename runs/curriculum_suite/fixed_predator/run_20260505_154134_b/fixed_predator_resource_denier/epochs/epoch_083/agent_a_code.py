def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

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

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if resources:
            # Choose resource that maximizes (opponent advantage after move)
            # Key for determinism: (-best_advantage, -closest_distance, nx, ny)
            best_adv = -10**9
            best_dist = 10**9
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                adv = do - ds  # positive means we're closer
                if adv > best_adv or (adv == best_adv and ds < best_dist) or (adv == best_adv and ds == best_dist and (rx, ry) < (best_dist, best_dist)):
                    best_adv = adv
                    best_dist = ds
            key = (-(best_adv), best_dist, nx, ny)
        else:
            # No resources: move to reduce distance to opponent (simple deterministic pressure)
            ds_opp = cheb(nx, ny, ox, oy)
            key = (ds_opp, nx, ny)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best else [0, 0]