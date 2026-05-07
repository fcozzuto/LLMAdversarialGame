def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(ox, oy)] if (0 <= ox < w and 0 <= oy < h and (ox, oy) not in obstacles) else [(sx, sy)]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dxdy = [0, 0]
    best_val = None

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        my = (nx, ny)
        # Choose the resource where we gain the most over opponent's distance
        best_adv = None
        best_my_dist = None
        for rx, ry in resources:
            res = (rx, ry)
            myd = man(my, res)
            opd = man((ox, oy), res)
            adv = opd - myd
            if best_adv is None or adv > best_adv or (adv == best_adv and myd < best_my_dist):
                best_adv = adv
                best_my_dist = myd

        # Higher is better: win the race (adv), then be close to secure faster.
        # Add tiny tie-break toward moving toward board center to avoid stalls.
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        center_bias = -0.001 * (abs(nx - cx) + abs(ny - cy))
        val = (10.0 * float(best_adv)) - float(best_my_dist) + center_bias

        if best_val is None or val > best_val:
            best_val = val
            best_dxdy = [dx, dy]

    return best_dxdy