def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(observation.get("obstacles", []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()

    def evader(r):
        r = r or ""
        return any(k in r for k in ("evader", "evade", "escape", "runner"))

    self_ev = evader(role)
    opp_ev = evader(opp_role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    res = observation.get("resources", None) or []
    if isinstance(res, dict):
        res = list(res.keys())
    res_list = [tuple(p) for p in res]

    def nearest_res_d2(px, py):
        if not res_list:
            return None
        best = None
        for rx, ry in res_list:
            if inb(rx, ry) and not blocked(rx, ry):
                d = dist2(px, py, rx, ry)
                if best is None or d < best:
                    best = d
        return best

    def valid_from(px, py):
        out = []
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if inb(nx, ny) and not blocked(nx, ny):
                out.append((dx, dy))
        return out

    my_d2r = nearest_res_d2(sx, sy)
    best_move = (0, 0)
    best_val = None

    cand = valid_from(sx, sy)
    if not cand:
        return [0, 0]

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        dopp = dist2(nx, ny, ox, oy)
        dres = nearest_res_d2(nx, ny)

        if self_ev:
            # Prefer resources; otherwise maximize distance from opponent.
            base = 0 if dres is None else (-dres)
            opp_term = -dopp
            if dres is None:
                opp_term = dopp
            val = base + opp_term
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            # Prefer resources; otherwise minimize distance from opponent.
            base = 0 if dres is None else (-dres)
            opp_term = dopp
            if dres is None:
                opp_term = -dopp
            val = base + opp_term
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)

    # Tiny 1-step lookahead to break ties deterministically against the opponent
    # (only if roles suggest pursuit/escape).
    if best_move != (0, 0) and (self_ev or opp_ev):
        dx0, dy0 = best_move
        nx0, ny0 = sx + dx0, sy + dy0
        opp_cands = valid_from(ox, oy)
        if opp_cands:
            def opp_score(px, py):
                # If opponent evader: maximize distance, else minimize distance.
                d = dist2(px, py, nx0, ny0)
                return d if opp_ev else -d

            best_opp = None
            best_opp_val =