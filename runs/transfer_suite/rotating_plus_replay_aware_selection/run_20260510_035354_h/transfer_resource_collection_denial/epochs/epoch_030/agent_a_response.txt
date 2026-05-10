def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = -10**9
    best_myd = 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Score by best "winning" resource: maximize (op_dist - my_dist), tie-break on my_dist.
        top_adv = -10**9
        top_myd = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            if adv > top_adv or (adv == top_adv and myd < top_myd):
                top_adv = adv
                top_myd = myd

        # If no resource yields positive advantage, still prefer smaller my distance and slightly larger opponent distance.
        fallback = top_myd - 0.05 * top_adv  # converts larger advantage to slightly better score when adv negative
        score = top_adv * 10 - fallback

        if score > best_score or (score == best_score and top_myd < best_myd):
            best_score = score
            best_myd = top_myd
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]