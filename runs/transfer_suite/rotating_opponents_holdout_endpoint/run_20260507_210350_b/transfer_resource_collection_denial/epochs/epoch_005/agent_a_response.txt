def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]

    best = None
    if resources:
        # Prefer resources where we are strictly closer (margin), then nearest such resource; otherwise chase closest available.
        for r in resources:
            if r in obstacles:
                continue
            ds = cheb((x, y), r)
            do = cheb((ox, oy), r)
            closer = 0 if ds < do else 1  # 0 better (we reach earlier)
            margin = (do - ds)  # larger better
            key = (closer, -margin, ds, r[0], r[1])
            if best is None or key < best[0]:
                best = (key, r)
        target = best[1]
    else:
        target = (w // 2, h // 2)

    tx, ty = target
    step_candidates = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            # Score step by progress toward target and by making it harder for opponent to take same cell next.
            d_self = cheb((nx, ny), (tx, ty))
            d_opp = cheb((ox, oy), (tx, ty))
            # Slight penalty if step moves directly toward opponent relative to target (reduces contention-free grabs).
            direct = 0
            if dx != 0:
                direct = 1 if (ox - x) * dx > 0 else 0
            if dy != 0:
                direct = 1 if (oy - y) * dy > 0 else direct
            key = (d_self, -((d_opp - d_self)), direct, nx, ny)
            step_candidates.append((key, [dx, dy]))
    if not step_candidates:
        return [0, 0]
    step_candidates.sort(key=lambda z: z[0])
    return step_candidates[0][1]