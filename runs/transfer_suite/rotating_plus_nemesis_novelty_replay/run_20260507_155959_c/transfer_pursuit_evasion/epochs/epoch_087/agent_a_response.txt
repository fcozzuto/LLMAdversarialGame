def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_evader = ("evad" in self_role) or ("runner" in self_role) or ("evasion" in self_role) or (self_role == "evader")
    opp_evader = ("evad" in opp_role) or ("runner" in opp_role) or ("evasion" in opp_role) or (opp_role == "evader")
    chase = (not self_evader) or opp_evader

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def clamp(v, lo, hi):
        if v < lo:
            return lo
        if v > hi:
            return hi
        return v

    tx = ox + (1 if ox > sx else (-1 if ox < sx else 0))
    ty = oy + (1 if oy > sy else (-1 if oy < sy else 0))
    tx = clamp(tx, 0, w - 1)
    ty = clamp(ty, 0, h - 1)

    cur_d2 = (sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d2o = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        md = abs(nx - ox) + abs(ny - oy)
        d2t = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))

        improvement = cur_d2 - d2o
        # Prefer moving into/near intercept target when chasing, else maximize distance
        val = 0.0
        if chase:
            val = (2.0 * improvement) - 0.6 * d2o - 0.35 * d2t + 0.05 * md + 0.01 * center
        else:
            val = (-2.0 * improvement) + 0.6 * d2o + 0.35 * d2t + 0.01 * center

        # Deterministic tie-breaker
        tie = (abs(nx - ox) + abs(ny - oy), abs(nx - tx) + abs(ny - ty), nx, ny, dx, dy)
        if best_val is None or val > best_val or (val == best_val and tie < best):
            best_val = val
            best = tie
            best_move = [dx, dy]

    return best_move if best_val is not None else [0, 0]