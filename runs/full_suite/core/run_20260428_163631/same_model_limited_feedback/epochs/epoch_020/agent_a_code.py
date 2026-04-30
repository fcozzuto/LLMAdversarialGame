def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation["grid_width"]
    h = observation["grid_height"]

    def cheb(a, b, c, d):
        da = a - c
        db = b - d
        if da < 0: da = -da
        if db < 0: db = -db
        return da if da > db else db

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None
    # Precompute for tie-breaking consistency
    res_sorted = sorted((rx, ry) for rx, ry in resources)
    for dx, dy in candidates:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            rd = None
            for rx, ry in res_sorted:
                d = cheb(nx, ny, rx, ry)
                if rd is None or d < rd:
                    rd = d
            oppd = cheb(ox, oy, nx, ny)
            # If we're very close to a resource, prioritize strongly; otherwise progress.
            score = -rd * 10 + oppd
        else:
            # No resources known: move away from opponent while drifting toward center-ish.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            drift = -cheb(nx, ny, cx, cy)
            oppd = cheb(ox, oy, nx, ny)
            score = oppd * 2 + drift

        tie = (dx, dy)
        if best_score is None or score > best_score or (score == best_score and tie < best):
            best_score = score
            best = tie

    if best is None:
        return [0, 0]
    return [best[0], best[1]]