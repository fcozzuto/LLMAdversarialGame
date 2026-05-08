def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def pick_target():
        if not resources:
            return (w // 2, h // 2)
        # Primary: resources we can reach no later than opponent; Secondary: maximize margin (we arrive earlier).
        best = None
        for r in resources:
            if r in obstacles:
                continue
            ds = dist((x, y), r)
            do = dist((ox, oy), r)
            # Prefer ds<=do, then smallest ds, then tie-break by coords
            tag = 0 if ds <= do else 1
            key = (tag, ds - do, ds, r[0], r[1])
            if best is None or key < best[0]:
                best = (key, r)
        return best[1] if best is not None else (w // 2, h // 2)

    target = pick_target()

    # Greedy step toward target; if target movement doesn't help relative race, pick best among steps by value.
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not free(nx, ny):
            continue
        # Value: after move, race advantage to current target; if equal, prefer getting closer and avoiding giving opponent advantage.
        ds = dist((nx, ny), target)
        do = dist((ox, oy), target)
        key = (ds - do, ds, abs(target[0] - nx) + abs(target[1] - ny), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    # If no move improves race (rare), take deterministic safe move: toward nearest resource by our distance.
    if best_key is None:
        return [0, 0]

    # Optional micro-adjust: if opponent is much closer to all resources, still choose step that minimizes their best capture distance.
    if resources:
        worst = None
        for r in resources:
            if r in obstacles:
                continue
            do = dist((ox, oy), r)
            if worst is None or do > worst[0]:
                worst = (do, r)
        if worst is not None:
            # Choose step that maximizes our distance from the opponent's closest resource (simple "denial by proximity").
            opp_best = worst[1]
            cur = dist((x, y), opp_best) - dist((ox, oy), opp_best)
            step_best = None
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not free(nx, ny):
                    continue
                val = dist((nx, ny), opp_best) - dist((ox, oy), opp_best)
                key = (-val, nx, ny)
                if step_best is None or key < step_best[0]:
                    step_best = (key, (dx, dy), val)
            if step_best is not None and step_best[2] > cur:
                best_move = step_best[1]

    return [best_move[0], best_move[1]]