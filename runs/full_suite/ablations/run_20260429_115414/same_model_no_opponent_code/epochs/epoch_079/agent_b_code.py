def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    center = ((w - 1) / 2.0, (h - 1) / 2.0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        if resources:
            val = -10**9
            for tx, ty in resources:
                ds = cheb(nx, ny, tx, ty)
                do = cheb(ox, oy, tx, ty)
                # Prefer resources where we are closer than opponent; slight push toward quick pickup.
                adv = (do - ds)
                tie_break = -(ds) - 0.05 * ((nx - center[0])**2 + (ny - center[1])**2) / ((w*h) or 1)
                # If we're already on a resource, strongly commit.
                on = 250 if (nx == tx and ny == ty) else 0
                v = adv * 20 + tie_break + on
                if v > val:
                    val = v
        else:
            tx, ty = int(round(center[0])), int(round(center[1]))
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            val = (do - ds) * 10 - ds - abs(nx - center[0]) - abs(ny - center[1])

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]