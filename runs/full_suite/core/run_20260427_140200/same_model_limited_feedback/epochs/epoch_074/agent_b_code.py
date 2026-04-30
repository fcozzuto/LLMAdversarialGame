def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))  # Chebyshev for 8-dir

    if not resources:
        # Drift toward center to avoid getting stuck
        tx, ty = w//2, h//2
        cand = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
        best = (10**9, 10**9, None)
        for dx, dy in cand:
            nx, ny = sx+dx, sy+dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d = dist((nx, ny), (tx, ty))
            key = (d, abs(nx-tx)+abs(ny-ty), (dx, dy))
            if key < best:
                best = (*key, (dx, dy))
        if best[2] is None:
            return [0, 0]
        return [best[2][0], best[2][1]]

    # Choose a target resource with a deterministic contest heuristic.
    best_t = None
    best_key = None
    for r in resources:
        mx = dist((sx, sy), r)
        oxd = dist((ox, oy), r)
        # Prefer resources where we are not far behind, and where we can reduce relative lead.
        key = (mx - 0.85 * oxd, mx, oxd, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best_t = r

    tx, ty = best_t
    cand = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best_step = None
    best = (10**9, 10**9, 10**9, None)
    cur_to_target = dist((sx, sy), (tx, ty))
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        dself = dist((nx, ny), (tx, ty))
        # Subtle defense: discourage stepping closer to opponent while not improving.
        dop = dist((nx, ny), (ox, oy))
        key = (dself, 0 if dself < cur_to_target else 1, dop, abs(nx-tx)+abs(ny-ty), dx, dy)
        if best_step is None or key < best:
            best = (*key, (dx, dy))
            best_step = (dx, dy)

    if best_step is None:
        return [0, 0]
    return [best_step[0], best_step[1]]