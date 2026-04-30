def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Greedy: pick a move that maximizes advantage (opponent distance - self distance) to the best available resource,
    # with a small tie-break for reducing distance to the closest resource.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dself_to_res = [man(nx, ny, rx, ry) for (rx, ry) in resources]
        dopp_to_res = [man(ox, oy, rx, ry) for (rx, ry) in resources]
        # Penalize moving next to obstacles to avoid getting trapped.
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obstacles:
                    adj_obs += 1

        best_resource_val = -10**18
        for ds, do in zip(dself_to_res, dopp_to_res):
            # Favor resources where we are closer than opponent (or at least by more).
            val = (do - ds) * 10 - ds
            if val > best_resource_val:
                best_resource_val = val

        closest_self = min(dself_to_res)
        overall = best_resource_val - adj_obs * 3 - closest_self * 0.1
        if overall > best_val:
            best_val = overall
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]