def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x, y, u, v):
        dx, dy = x - u, y - v
        return dx * dx + dy * dy

    legal_self = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal_self.append((dx, dy, nx, ny))
    if not legal_self:
        return [0, 0]

    best = (10**18, 0, 0)
    for dx, dy, nsx, nsy in legal_self:
        if nsx == ox and nsy == oy:
            return [dx, dy]  # immediate capture

        # opponent chooses move to maximize our distance after their move
        worst_dist = -1
        legal_opp = []
        for odx, ody in dirs:
            nox, noy = ox + odx, oy + ody
            if inb(nox, noy):
                legal_opp.append((nox, noy))
        if not legal_opp:
            legal_opp = [(ox, oy)]

        for nox, noy in legal_opp:
            # if opponent moves onto us, capture would have occurred earlier; ignore (no capture for us)
            d = dist2(nsx, nsy, nox, noy)
            if d > worst_dist:
                worst_dist = d

        # tie-break deterministically toward decreasing distance to opponent
        d_now = dist2(sx, sy, ox, oy)
        d_next_min = worst_dist
        val = (d_next_min, -d_now)
        if val < (best[0], best[1]):
            best = (val[0], val[1], dx * 3 + dy)  # deterministic tie-break id

    # reconstruct move from tie-break id: prefer simpler mapping by scanning again
    # Since best stores only a scalar tie id, rescan to find matching best primary value and tie
    target_d = best[0]
    target_tie = best[2]
    chosen = [0, 0]
    best_pair = None
    for dx, dy, nsx, nsy in legal_self:
        if nsx == ox and nsy == oy:
            return [dx, dy]
        worst_dist = -1
        for odx, ody in dirs:
            nox, noy = ox + odx, oy + ody
            if inb(nox, noy):
                d = dist2(nsx, nsy, nox, noy)
                if d > worst_dist:
                    worst_dist = d
        if worst_dist == target_d:
            tie = dx * 3 + dy
            if tie == target_tie:
                chosen = [dx, dy]
                break
        if best_pair is None or (worst_dist, dx * 3 + dy) < best_pair:
            best_pair = (worst_dist, dx * 3 + dy)
            chosen = [dx, dy]
    return chosen