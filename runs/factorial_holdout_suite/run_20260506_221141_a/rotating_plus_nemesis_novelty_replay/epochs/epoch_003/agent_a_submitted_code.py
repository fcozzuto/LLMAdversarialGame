def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(obstacles)

    def free(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        best = (0, 0, 10**18)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            score = (abs(nx - ox) + abs(ny - oy))
            if score > best[2] or (score == best[2] and (dx, dy) < (best[0], best[1])):
                best = (dx, dy, score)
        return [best[0], best[1]]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_self = 10**18
        d_opp = 10**18
        for rx, ry in resources:
            ds = abs(nx - rx) + abs(ny - ry)
            if ds < d_self:
                d_self = ds
            do = abs(ox - rx) + abs(oy - ry)
            if do < d_opp:
                d_opp = do
        # Prefer reducing distance to resources; discourage giving opponent advantage.
        val = (d_self * 1000) - (d_opp * 1) + (1 if (nx, ny) in resources else 0) * -1
        cand = (val, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best is None or cand < best:
            best = cand

    return [best[2], best[3]]