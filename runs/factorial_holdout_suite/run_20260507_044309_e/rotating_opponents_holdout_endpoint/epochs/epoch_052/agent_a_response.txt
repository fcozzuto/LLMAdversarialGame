def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def obs_pen(x, y):
        if (x, y) in obstacles:
            return 10**6
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (x + dx, y + dy) in obstacles:
                    p += 3
        return p

    # Focus on closest resources to reduce work and noise
    res_sorted = sorted(resources, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))
    res_sorted = res_sorted[:6]

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_delta = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        p = obs_pen(nx, ny)
        # Prefer cells that maximize our closeness advantage over opponent for some resource
        max_gap = -10**18
        best_res_d = 10**18
        for r in res_sorted:
            d_self = dist((nx, ny), r)
            d_opp = dist((ox, oy), r)
            gap = d_opp - d_self  # bigger => we are closer
            if gap > max_gap or (gap == max_gap and d_self < best_res_d):
                max_gap = gap
                best_res_d = d_self

        # If we can get closer right now, prioritize; also discourage wandering
        val = max_gap * 1000 - best_res_d - p
        if val > best_val:
            best_val = val
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]