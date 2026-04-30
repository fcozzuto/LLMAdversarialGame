def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = observation["resources"]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if resources:
        best = None
        # Prefer a resource we are closer to than opponent; otherwise nearest.
        for i, r in enumerate(resources):
            rx, ry = r
            if (rx, ry) in obstacles:
                continue
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # score key: lower is better; strong preference if we are not losing
            key = (1 if ds <= do else 0, ds, -do, i, rx, ry)
            if best is None or key < best[0]:
                best = (key, r)
        target = best[1]
    else:
        # No resources: go to center-ish
        target = (w // 2, h // 2)

    tx, ty = target
    cur_d = dist((sx, sy), (tx, ty))

    def step_toward():
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return dx, dy

    direct = step_toward()
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = dist((nx, ny), (tx, ty))
            # Prefer moves that decrease distance; break ties deterministically
            candidates.append((d, abs(dx) + abs(dy), nx, ny, dx, dy))
    candidates.sort()
    if candidates:
        # If direct doesn't worsen much, keep the best move anyway (stable, deterministic)
        if direct not in [(c[4], c[5]) for c in candidates[:3]]:
            return [candidates[0][4], candidates[0][5]]
        # Still choose the best candidate deterministically
        return [candidates[0][4], candidates[0][5]]

    return [0, 0]