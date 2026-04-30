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

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dx, best_dy, bestv = 0, 0, -10**18
    oppd = cheb(sx, sy, ox, oy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        v = 0.0
        # Avoid getting too close to opponent unless it helps contest resources.
        v += 0.10 * cheb(nx, ny, ox, oy)
        v -= 0.02 * cheb(nx, ny, w // 2, h // 2)

        if resources:
            for r in resources:
                if not r or len(r) < 2:
                    continue
                rx, ry = r[0], r[1]
                if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in obs:
                    continue
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                gap = do - ds  # positive => we are closer than opponent
                # If we can arrive sooner or tie, strongly favor; otherwise mildly avoid.
                if gap >= 0:
                    v += 3.0 * gap
                else:
                    v += 0.7 * gap
                v -= 0.08 * ds

            # If opponent is closer to all resources, prioritize shrinking our worst distance.
            min_gap = 10**9
            for r in resources:
                if not r or len(r) < 2:
                    continue
                rx, ry = r[0], r[1]
                if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in obs:
                    continue
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                g = do - ds
                if g < min_gap:
                    min_gap = g
            if min_gap < 0:
                v -= 0.35 * (-min_gap)

        else:
            # No visible resources: drift toward nearest safe center-ish point and away from obstacles by favoring higher distance from opponent.
            v += 0.05 * cheb(nx, ny, ox, oy)
            v += 0.01 * cheb(nx, ny, sx, sy)

        # Small bias to keep moving when not improving: encourage actions that increase distance from opponent if they are closer.
        if oppd < 3:
            v += 0.08 * cheb(nx, ny, ox, oy)

        if v > bestv:
            bestv = v
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]