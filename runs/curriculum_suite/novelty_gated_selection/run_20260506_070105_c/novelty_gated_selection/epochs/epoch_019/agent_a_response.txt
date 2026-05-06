def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    # Pick opponent's likely target: closest resource to opponent.
    tx, ty = min(resources, key=lambda r: man(ox, oy, r[0], r[1]))

    # Predict opponent's next greedy move toward that target.
    best_om = (0, 0)
    best_od = 10**9
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = ox, oy
        d = man(nx, ny, tx, ty)
        if d < best_od or (d == best_od and (dx, dy) < best_om):
            best_od, best_om = d, (dx, dy)
    nox, noy = ox + best_om[0], oy + best_om[1]
    if not inb(nox, noy) or (nox, noy) in obstacles:
        nox, noy = ox, oy

    # Evaluate self moves: take priority on reaching target first; add interception pressure.
    best = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        my_t = man(nx, ny, tx, ty)
        opp_t = man(nox, noy, tx, ty)
        if resources:
            # Secondary: avoid letting opponent steal other close resources by drifting too far.
            my_any = min(man(nx, ny, rx, ry) for rx, ry in resources)
            opp_any = min(man(nox, noy, rx, ry) for rx, ry in resources)
        else:
            my_any = opp_any = 0

        # Intercept bonus: move to where our next position can contest their next position.
        inter = man(nx, ny, nox, noy)

        score = (opp_t - my_t) * 5.0 + (my_any - my_t) * -0.2 + (opp_any - my_any) * 0.6 - inter * 0.35

        # Deterministic tie-break favoring progress toward target, then lower dx/dy lexicographically.
        if score > best_score or (score == best_score and (my_t, dx, dy) < (man(sx + best[0], sy + best[1], tx, ty), best[0], best[1])):
            best_score = score
            best = [dx, dy]

    return best