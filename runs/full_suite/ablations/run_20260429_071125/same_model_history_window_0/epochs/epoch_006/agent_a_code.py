def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    res_set = set((p[0], p[1]) for p in resources)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(a, b, c, d): return abs(a - c) + abs(b - d)

    # Choose a target resource to contest
    if resources:
        best = None
        bestv = -10**18
        for rx, ry in resources:
            ds = md(sx, sy, rx, ry)
            do = md(ox, oy, rx, ry)
            v = (do - ds) * 10 - ds  # higher when we're closer
            if v > bestv or (v == bestv and ds < best[0]):
                bestv = v
                best = (ds, rx, ry)
        tx, ty = best[1], best[2]
    else:
        # No resources: head to opponent to deny/pressure
        tx, ty = ox, oy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestscore = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds2 = md(nx, ny, tx, ty)
        do2 = md(ox, oy, tx, ty)
        # If landing on a resource, strongly prefer it
        on_res = 1 if (nx, ny) in res_set else 0
        # Prefer shrinking distance to target; slightly discourage moving away from contested advantage
        score = -ds2 * 10 + on_res * 1000 + (do2 - ds2) * 2 - md(nx, ny, ox, oy) * 0.1
        if score > bestscore or (score == bestscore and (dx, dy) < bestm):
            bestscore = score
            bestm = (dx, dy)

    dx, dy = bestm
    return [dx, dy]