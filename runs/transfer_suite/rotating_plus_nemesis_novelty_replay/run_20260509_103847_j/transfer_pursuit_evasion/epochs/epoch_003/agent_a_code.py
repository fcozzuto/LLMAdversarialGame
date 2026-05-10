def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)

    rolestr = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in rolestr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves_self = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            moves_self.append((dx, dy))

    moves_opp = []
    for dx, dy in deltas:
        nx, ny = ox + dx, oy + dy
        if valid(nx, ny):
            moves_opp.append((dx, dy))
    if not moves_self:
        moves_self = [(0, 0)]
    if not moves_opp:
        moves_opp = [(0, 0)]

    best_move = (0, 0)
    best_val = None
    for sdx, sdy in moves_self:
        nsx, nsy = sx + sdx, sy + sdy
        # distance^2 after both move
        if is_evader:
            # pursuer tries to minimize distance
            mind = None
            for odx, ody in moves_opp:
                nox, noy = ox + odx, oy + ody
                d2 = (nsx - nox) * (nsx - nox) + (nsy - noy) * (nsy - noy)
                if mind is None or d2 < mind:
                    mind = d2
            val = mind
            if best_val is None or val > best_val:
                best_val, best_move = val, (sdx, sdy)
        else:
            # evader tries to maximize distance
            maxd = None
            for odx, ody in moves_opp:
                nox, noy = ox + odx, oy + ody
                d2 = (nsx - nox) * (nsx - nox) + (nsy - noy) * (nsy - noy)
                if maxd is None or d2 > maxd:
                    maxd = d2
            val = maxd
            if best_val is None or val < best_val:
                best_val, best_move = val, (sdx, sdy)

    return [int(best_move[0]), int(best_move[1])]