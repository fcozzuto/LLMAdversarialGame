def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    occ = set((p[0], p[1]) for p in obstacles)
    if resources:
        def dist(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        best_r = None
        best_val = -10**9
        for rx, ry in resources:
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources where we are closer than opponent (or least worse),
            # with a small bias toward central-ish cells.
            center_bias = -(abs(rx - (gw - 1) / 2) + abs(ry - (gh - 1) / 2)) * 0.05
            val = (do - ds) + center_bias
            if val > best_val:
                best_val = val
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        # Fallback: move toward center while avoiding obstacles
        tx, ty = (gw - 1) / 2, (gh - 1) / 2

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= gw or ny >= gh:
            continue
        if (nx, ny) in occ:
            continue
        # Compute objective: get closer to target, and keep away from opponent a bit
        ds = abs(nx - tx) + abs(ny - ty)
        do = abs(nx - ox) + abs(ny - oy)
        # Avoid stepping adjacent to obstacles (soft penalty)
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in occ:
                    adj_pen = 1
        candidates.append((ds, -do + adj_pen, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (t[0], t[1]))
    return [candidates[0][2], candidates[0][3]]