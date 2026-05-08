def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr)
    opp_is_evader = ("evader" in orr) or ("runner" in orr)

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def step_from(tx, ty, dx, dy):
        nx, ny = tx + dx, ty + dy
        if free(nx, ny):
            return nx, ny
        return tx, ty

    def manhattan(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    for dx, dy in moves:
        nsx, nsy = step_from(sx, sy, dx, dy)
        if nsx == ox and nsy == oy:
            return [dx, dy]  # immediate capture (pursuer) or avoid if evader below

        # predict opponent response greedily
        best_opp = None
        for odx, ody in moves:
            nox, noy = step_from(ox, oy, odx, ody)
            d = manhattan(nsx, nsy, nox, noy)
            # evader maximizes distance, pursuer minimizes distance
            sc = d if opp_is_evader else -d
            if best_opp is None or sc > best_opp[0]:
                best_opp = (sc, nox, noy)
        nox, noy = best_opp[1], best_opp[2]
        d_after = manhattan(nsx, nsy, nox, noy)

        # score: capture is best for pursuer, worst for evader; otherwise distance objective
        if not self_is_evader:
            val = (1e6 if (nox == nsx and noy == nsy) else 0) + (-d_after)
        else:
            val = (-1e6 if (nox == nsx and noy == nsy) else 0) + (d_after)

        if best is None:
            best = (val, dx, dy)
        else:
            if val > best[0]:
                best = (val, dx, dy)
            elif val == best[0]:
                # deterministic tie-break: prefer staying still less, then lexicographic
                if (dx, dy) < (best[1], best[2]):
                    best = (val, dx, dy)

    return [best[1], best[2]]