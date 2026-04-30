def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    if not resources:
        tx = (w - 1 - sx + sx + 0) // 1  # deterministic no-op fallback target
        ty = (h - 1 - sy + sy + 0) // 1
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if dx == 0 and dy == 0:
                    cand = dist2((nx, ny), (ox, oy))
                else:
                    if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                        continue
                    cand = dist2((nx, ny), (ox, oy))
                if best is None or cand < best[0]:
                    best = (cand, dx, dy)
        return [best[1], best[2]]

    # Choose resource where we are relatively closer than opponent.
    best_res = None
    best_key = None
    for r in resources:
        r = (r[0], r[1])
        ds = dist2((sx, sy), r)
        do = dist2((ox, oy), r)
        # Higher is better: opponent farther and/or we closer.
        key = (do - ds, -ds, -(abs(r[0] - w // 2) + abs(r[1] - h // 2)), r[0], r[1])
        if best_key is None or key > best_key:
            best_key = key
            best_res = r

    tx, ty = best_res
    options = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            # Prefer getting closer to target and not letting opponent approach too much.
            ns = dist2((nx, ny), (tx, ty))
            no = dist2((ox, oy), (tx, ty))
            # Also avoid stepping onto/adjacent to opponent unless it improves target distance a lot.
            adj_opp = max(abs(nx - ox), abs(ny - oy))
            score = (ns, adj_opp, no - ns, dx, dy)
            options.append((score, dx, dy, nx, ny))

    # Deterministic: minimize score tuple.
    options.sort(key=lambda z: z[0])
    return [options[0][1], options[0][2]]