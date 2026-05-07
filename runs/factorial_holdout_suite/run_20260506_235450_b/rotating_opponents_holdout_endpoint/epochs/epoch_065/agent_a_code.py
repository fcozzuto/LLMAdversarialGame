def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
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

    def man(a, b, x, y):
        return abs(a - x) + abs(b - y)

    # Prefer moves that let us be closer than opponent to an attractive "contested" resource.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate best contested target from (nx, ny)
        local_best = -10**18
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Contention: we want opp farther than us; also prefer targets we can reach soon.
            # Small bias to avoid drifting when distances tie.
            val = (opp_d - self_d) * 100 - self_d
            # Additional tie-break: prefer resources more "towards opponent corner" to pressure their route.
            val += (rx + ry) * 0.01 - (abs(rx - ox) + abs(ry - oy)) * 0.001
            if val > local_best:
                local_best = val

        # Global tie-break: prefer closer overall if contention is equal.
        overall = local_best * 1000 - man(nx, ny, ox, oy) - man(nx, ny, sx, sy) * 0.001
        if overall > best_val:
            best_val = overall
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]