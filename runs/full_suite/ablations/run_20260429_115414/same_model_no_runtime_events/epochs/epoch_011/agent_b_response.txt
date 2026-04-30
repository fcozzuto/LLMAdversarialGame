def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    valid_res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = r[0], r[1]
            if ok(x, y):
                valid_res.append((x, y))

    best = (0, 0)
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Defensive/spacing: don't step too close to opponent.
        opp_dist = cheb(nx, ny, ox, oy)
        v = 0.6 * opp_dist

        if valid_res:
            # Offensive: contest resources only if we arrive earlier.
            local = 0
            for rx, ry in valid_res:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer resources where we are clearly earlier, penalize those opponent can grab first.
                if ds <= do - 1:
                    local += 10 / (1 + ds)
                elif do <= ds:
                    local -= 8 / (1 + ds)
                else:
                    local += 1 / (1 + ds)
                # Small shaping toward overall closeness to remaining resources.
                local += 0.08 * (do - ds)
            v += local

        # If no resources, drift away from opponent toward edges (deterministic).
        else:
            v += 0.1 * (nx + ny)  # corners bias

        if v > bestv:
            bestv = v
            best = (dx, dy)

    dx, dy = best
    if not (dx in (-1, 0, 1) and dy in (-1, 0, 1)):
        return [0, 0]
    if not ok(sx + dx, sy + dy):
        return [0, 0]
    return [dx, dy]