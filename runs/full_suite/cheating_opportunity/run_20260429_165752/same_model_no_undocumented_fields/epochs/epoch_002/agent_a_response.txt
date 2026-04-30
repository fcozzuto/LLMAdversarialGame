def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(tuple(o) for o in observation.get("obstacles", []))

    if (x, y) in resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    deltas = [(0, 0), (1, 1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (-1, -1)]
    order = deltas

    best_delta = (0, 0)
    best_key = None

    # Strategy: choose a target resource that favors us vs opponent, then take the move that best improves that target.
    def pick_target():
        if not resources:
            return (w // 2, h // 2)
        best = None
        best_score = None
        for r in resources:
            ds = dist((x, y), r)
            do = dist((ox, oy), r)
            score = ds - 0.85 * do  # smaller is better: be closer than opponent
            key = (score, ds, r[0], r[1])
            if best_score is None or key < best_key:
                return r
        return best if best is not None else resources[0]

    target = resources[0] if resources else (w // 2, h // 2)
    if resources:
        best_key = None
        best_target = None
        for r in resources:
            ds = dist((x, y), r)
            do = dist((ox, oy), r)
            score = ds - 0.85 * do
            key = (score, ds, r[0], r[1])
            if best_key is None or key < best_key:
                best_key = key
                best_target = r
        target = best_target

    tx, ty = target
    for dx, dy in order:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate: progress to target, while not letting opponent get too much closer to target resources.
        d_self_t = dist((nx, ny), target)
        d_op_t = dist((ox, oy), target)
        # If we can grab a resource immediately, prioritize it strongly.
        immediate = 1 if (nx, ny) in resources else 0

        # Secondary: if resources exist, include a small "threat" term for closest rival-attracting resources.
        threat = 0
        if resources:
            # deterministic: compute best (small ds - 0.85*do) from opponent perspective after our move
            best_r_key = None
            for r in resources:
                ds2 = dist((nx, ny), r)
                do2 = dist((ox, oy), r)
                k = (ds2 - 0.85 * do2, ds2, r[0], r[1])
                if best_r_key is None or k < best_r_key:
                    best_r_key = k
                    threat = k[0]
        # Lower is better: immediate > progress > global threat.
        key = (-immediate, d_self_t, threat, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]