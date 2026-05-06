def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w, h = observation["grid_width"], observation["grid_height"]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        # Stay centered-ish while keeping distance from opponent
        best = None
        bestk = None
        for dx, dy, nx, ny in legal:
            k = (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2), abs(nx - ox) + abs(ny - oy))
            if bestk is None or k < bestk:
                bestk = k
                best = (dx, dy)
        return [best[0], best[1]]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # When close to opponent, prefer moves that reduce opponent distance to nearest resource we can take.
    dso = man(sx, sy, ox, oy)

    best = None
    bestk = None
    for dx, dy, nx, ny in legal:
        best_res_score = None
        # Greedy pick: best resource we can reach soon while discounting resources opponent is closer to.
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_me = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            if d_op < d_me:
                # Opponent favors it: penalize, but allow if we are only slightly behind.
                penalty = (d_me - d_op) * 4 + 8
            else:
                penalty = 0
            # Encourage taking closer resources and staying away from opponent when not contesting.
            base = d_me * 1.5 + penalty
            # If very close to opponent, bias towards contesting by minimizing distance to opponent while not leaving resources.
            if dso <= 2:
                base += man(nx, ny, ox, oy) * 0.8
            # Mild tie-break: prefer moves that advance toward board corners (more lanes for resources).
            base += 0.05 * (min(nx, w - 1 - nx) + min(ny, h - 1 - ny))
            score = base
            if best_res_score is None or score < best_res_score:
                best_res_score = score
        if best_res_score is None:
            continue
        # Prefer also not stepping directly into opponent proximity.
        k = (best_res_score, man(nx, ny, ox, oy), abs(nx - sx) + abs(ny - sy))
        if bestk is None or k < bestk:
            bestk = k
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]