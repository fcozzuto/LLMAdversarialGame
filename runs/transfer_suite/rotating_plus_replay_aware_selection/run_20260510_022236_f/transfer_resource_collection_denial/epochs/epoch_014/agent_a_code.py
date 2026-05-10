def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs_set = set((x, y) for x, y in obstacles)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # If no resources exist, just hold.
    if not resources:
        return [0, 0]

    # Deterministic tie-break preference order (stable iteration already).
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        # Evaluate contested advantage across all remaining resources.
        cell_val = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Positive means we can reach sooner than opponent.
            adv = od - sd
            # Prefer resources we are already close to; strongly prefer immediate capture.
            immediate = 10**6 if (nx == rx and ny == ry) else 0
            score = adv * 1000 + immediate * 2 + (2000 // (sd + 1))
            if score > cell_val:
                cell_val = score

        # Mild safety: discourage stepping away if opponent is extremely close to some resource.
        # (This changes behavior when advantage is negative.)
        min_opp = 10**9
        for rx, ry in resources:
            od = cheb(ox, oy, rx, ry)
            if od < min_opp:
                min_opp = od
        if min_opp <= 1:
            my_best = 10**9
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                if sd < my_best:
                    my_best = sd
            cell_val -= my_best * 50

        if cell_val > best_val:
            best_val = cell_val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]