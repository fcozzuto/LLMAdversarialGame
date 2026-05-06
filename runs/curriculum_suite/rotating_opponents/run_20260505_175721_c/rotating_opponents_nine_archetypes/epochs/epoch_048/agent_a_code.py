def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # pick the most "swingy" target for this move
        best_adv = -10**9
        best_dist = 10**9
        best_r = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer
            if adv > best_adv or (adv == best_adv and (sd < best_dist or (sd == best_dist and (rx, ry) < best_r))):
                best_adv = adv
                best_dist = sd
                best_r = (rx, ry)

        # contest if we can't get advantage: move toward resource we're closest to
        if best_adv < 0:
            # compute our closest resource distance for fallback
            closest = 10**9
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if d < closest:
                    closest = d
            # also reduce moves that let opponent be very close to that closest target
            # approximate by considering opponent distance to our nearest resource's nearest
            ox_to_nearest = 10**9
            for rx, ry in resources:
                if man(nx, ny, rx, ry) == closest:
                    ox_to_nearest = min(ox_to_nearest, man(ox, oy, rx, ry))
            score = -closest - 2 * ox_to_nearest  # smaller is better for opponent closeness
        else:
            # strong contest: emphasize advantage heavily, then nearest
            score = -best_dist - 5 * best_adv

        # deterministic tie-break
        key = (score, abs(nx - ox) + abs(ny - oy), nx, ny, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]] if best else [0, 0]