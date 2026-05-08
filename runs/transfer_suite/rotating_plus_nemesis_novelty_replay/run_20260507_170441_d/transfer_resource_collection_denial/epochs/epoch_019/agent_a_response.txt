def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set((p[0], p[1]) for p in obstacles)

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**30
    rset = set((r[0], r[1]) for r in resources)

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            continue

        cur_dmin = 10**18
        best_rel = -10**18
        best_opp_closest = 10**18

        for rx, ry in resources:
            myd = d2(nx, ny, rx, ry)
            opd = d2(ox, oy, rx, ry)
            rel = opd - myd
            if rel > best_rel:
                best_rel = rel
            if myd < cur_dmin:
                cur_dmin = myd
            odmin = d2(ox, oy, rx, ry)
            if odmin < best_opp_closest:
                best_opp_closest = odmin

        # encourage stepping onto a resource; otherwise, move to improve relative closeness
        val = best_rel
        if (nx, ny) in rset:
            val += 10**9
        # if we can't beat the opponent anywhere, focus on denying their nearest resource
        if best_rel < 0:
            val += (best_opp_closest - cur_dmin) * 0.001

        # deterministic tie-break: prefer smaller distance to some resource, then lexicographic move
        if val > best_val or (val == best_val and (cur_dmin, dx, dy) < (1 * (best_val == best_val), best_move[0], best_move[1])):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]