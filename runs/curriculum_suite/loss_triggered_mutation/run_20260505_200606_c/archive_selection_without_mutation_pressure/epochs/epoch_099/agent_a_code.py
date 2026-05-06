def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Corner pressure: after some resources collected, bias toward far-side sweep where opponent less likely.
    rc = observation.get("remaining_resource_count", len(res))
    late = 1 if rc <= len(res) // 3 else 0
    target_corner = (w - 1, h - 1) if (sy + sx) % 2 == 0 else (0, h - 1)

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Immediate safe/avoid: discourage moving closer to opponent unless it improves our chance on resources.
        dist_opp_now = man(nx, ny, ox, oy)
        dist_opp_prev = man(sx, sy, ox, oy)
        opp_pen = 0
        if dist_opp_now < dist_opp_prev:
            opp_pen = 0.7

        val = -opp_pen
        # Resource competition: maximize (opponent worse + ours better), prefer nearer resources.
        for rx, ry in res:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds == 0:
                # landing on a resource is decisive
                val += 10_000
                continue
            # If we can undercut opponent on this resource, reward strongly.
            undercut = do - ds  # positive if we are closer
            val += (undercut * 25.0) / (1 + ds)
            # Small preference to reduce our distance even if opponent is also close.
            val += 8.0 / (1 + ds)
            # Slightly penalize going toward resources the opponent is already far ahead on.
            if undercut < 0:
                val -= (-undercut) * 1.5 / (1 + ds)

        if late:
            # Late-game: push toward a corner to secure remaining resources.
            val += 3.0 * (man(sx, sy, target_corner[0], target_corner[1]) - man(nx, ny, target_corner[0], target_corner[1])) / (1 + man(nx, ny, target_corner[0], target_corner[1]))

        # Prefer moves that keep us from being immediately adjacent to opponent (unless we are on top of a resource).
        if dist_opp_now == 1:
            val -= 5.0

        if val > best[0] or (val == best[0] and (dx, dy) < (best[1], best[2])):
            best = (val, dx, dy)

    return [int(best[1]), int(best[2])]