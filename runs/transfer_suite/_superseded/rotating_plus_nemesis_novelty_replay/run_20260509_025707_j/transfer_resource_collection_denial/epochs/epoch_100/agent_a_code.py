def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Aim to beat opponent on the best contestable resource from the next position.
        best_local = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; large bonus for contests we win.
            val = (do - ds) * 10 - ds
            # If opponent is closer, still move toward it only if it's our closest option.
            if do < ds:
                val -= (ds - do) * 3
            # Small bias toward center-ish to avoid dithering.
            val -= (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)) * 0.01
            if val > best_local:
                best_local = val

        # Secondary tie-break: prefer reducing distance to the globally nearest resource.
        if best_local > best[1]:
            best = ((dx, dy), best_local)
        elif best_local == best[1] and best[0] is not None:
            cur_dist = min(man(nx, ny, rx, ry) for rx, ry in resources)
            bx, by = best[0]
            nx2, ny2 = sx + bx, sy + by
            prev_dist = min(man(nx2, ny2, rx, ry) for rx, ry in resources)
            if cur_dist < prev_dist:
                best = ((dx, dy), best_local)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]