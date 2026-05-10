def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        best = None
        for r in resources:
            d = dist((sx, sy), r)
            key = (d, r[0], r[1])
            if best is None or key < best[0]:
                best = (key, r)
        tx, ty = best[1]
        def step_options():
            opts = []
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    nx, ny = sx + dx, sy + dy
                    if dx == 0 and dy == 0:
                        continue
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                        nd = dist((nx, ny), (tx, ty))
                        opts.append((nd, nx, ny, dx, dy))
            return opts

        # primary: move closer if possible
        opts = step_options()
        if opts:
            opts.sort(key=lambda z: (z[0], z[1], z[2], z[3], z[4]))
            if opts[0][0] <= dist((sx, sy), (tx, ty)):
                return [opts[0][3], opts[0][4]]

        # secondary: greedy toward target with diagonal preference, even if it increases temporarily
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]

        # fallback: any safe move that doesn't increase distance to opponent too much
        best2 = None
        for dy2 in (-1, 0, 1):
            for dx2 in (-1, 0, 1):
                if dx2 == 0 and dy2 == 0:
                    continue
                nx2, ny2 = sx + dx2, sy + dy2
                if 0 <= nx2 < w and 0 <= ny2 < h and (nx2, ny2) not in obstacles:
                    d_to_target = dist((nx2, ny2), (tx, ty))
                    d_to_opp = dist((nx2, ny2), (ox, oy))
                    key = (d_to_target, d_to_opp, nx2, ny2)
                    if best2 is None or key < best2[0]:
                        best2 = (key, [dx2, dy2])
        if best2 is not None:
            return best2[1]

    # No resources: head to center or away from immediate obstacle pressure deterministically
    cx, cy = (w - 1) // 2, (h - 1) // 2
    dx = 0 if cx == sx else (1 if cx > sx else -1)
    dy = 0 if cy == sy else (1 if cy > sy else -1)
    nx, ny = sx + dx, sy + dy
    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
        return [dx, dy]

    # final fallback: try any safe move with deterministic tie-break; else stay
    best3 = None
    for dy2 in (-1, 0, 1):
        for dx2 in (-1, 0, 1):
            if dx2 == 0 and dy2 == 0:
                continue
            nx2, ny2 = sx + dx2, sy + dy2
            if 0 <= nx2 < w and 0 <= ny2 < h and (nx2, ny2) not in obstacles:
                key = (abs(nx2 - cx) + abs(ny2 - cy), nx2, ny2)
                if best3 is None or key < best3[0]:
                    best3 = (key, [dx2, dy2])
    return best3[1] if best3 is not None else [0, 0]