def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    if not resources:
        return [0, 0]

    obs = set((p[0], p[1]) for p in obstacles)
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a priority resource: first one I can reach no worse than opponent; otherwise, least-bad contest.
    best_r = None
    best_key = None
    for rx, ry in resources:
        md = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (1 if md > od else 0, md - od, md, rx, ry)
        if best_key is None or key < best_key:
            best_key, best_r = key, (rx, ry)

    tx, ty = best_r

    # Opponent one-step prediction: greedy to its nearest resource (obstacle-aware).
    def opp_next():
        best_move = (0, 0)
        best_dist = None
        for dx, dy in deltas:
            nx, ny = ox + dx, oy + dy
            if not inb(nx, ny):
                continue
            # nearest resource distance after opponent move
            nd = min(man(nx, ny, rx, ry) for rx, ry in resources)
            if best_dist is None or nd < best_dist or (nd == best_dist and (dx, dy) < best_move):
                best_dist = nd
                best_move = (dx, dy)
        return best_move

    pdx, pdy = opp_next()

    # Evaluate our moves by improving our advantage on the priority resource vs opponent's predicted move.
    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_after = man(nx, ny, tx, ty)
        opp_after = man(ox + pdx, oy + pdy, tx, ty)
        # Advantage: smaller is better for opponent; we maximize (opp - my), tie-break by closer to target.
        val = (opp_after - my_after, -my_after, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]