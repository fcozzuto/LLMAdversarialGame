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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_evader = ("evad" in self_role) or ("runner" in self_role) or ("evasion" in self_role) or (self_role == "evader")
    opp_evader = ("evad" in opp_role) or ("runner" in opp_role) or ("evasion" in opp_role) or (opp_role == "evader")
    pursuing = (not self_evader) or opp_evader

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x, y):
        return max(abs(x - ox), abs(y - oy))

    best_dx, best_dy = 0, 0
    if pursuing:
        best = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue
            d = cheb(nx, ny)
            # Strongly prefer immediate capture (exact cell collision).
            if nx == ox and ny == oy:
                return [dx, dy]
            # Deterministic tie-break: prefer moves that keep/approach using squared Euclid.
            ddx, ddy = nx - ox, ny - oy
            tie = ddx * ddx + ddy * ddy
            if d < best or (d == best and tie < (best_dy + 1) * 10**6):
                best = d
                best_dx, best_dy = dx, dy
    else:
        best = -1
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue
            d = cheb(nx, ny)
            # Avoid capture if possible.
            if nx == ox and ny == oy:
                continue
            # Tie-break deterministically by squared Euclid.
            ddx, ddy = nx - ox, ny - oy
            tie = ddx * ddx + ddy * ddy
            if d > best or (d == best and tie > best):
                best = d
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]