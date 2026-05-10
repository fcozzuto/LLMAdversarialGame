def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def sqdist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy
    def adjsets(x, y):
        a_opp = a_self = a_obs = False
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not inb(nx, ny):
                    continue
                if (nx, ny) in obs:
                    a_obs = True
                elif (nx, ny) in opp_terr:
                    a_opp = True
                elif (nx, ny) in self_terr:
                    a_self = True
        return a_opp, a_self, a_obs

    # Pick best frontier-ish unclaimed cell (adjacent to opponent), else any unclaimed
    best = None
    opp_pos = (ox, oy)
    for (x, y) in unclaimed:
        if (x, y) in obs:
            continue
        a_opp, a_self, a_obs = adjsets(x, y)
        base = 0
        if a_opp:
            base += 200
        elif a_self:
            base += 40
        base += 10
        # Prefer cells closer to us (so we can capture) but not too close to opponent
        d_me = sqdist((x, y), (sx, sy))
        d_opp = sqdist((x, y), opp_pos)
        val = base - d_me * 0.5 + min(d_opp, 64) * 0.15
        if a_obs:
            val -= 25
        key = (val, -x, -y)  # deterministic tie-break
        if best is None or key > best[0]:
            best = (key, (x, y))

    target = best[1] if best is not None else (sx, sy)

    # Move one step toward target, but never into obstacles (engine would keep us, so avoid)
    tx, ty = target
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = -sqdist((nx, ny), (tx, ty))
        # If stepping onto opponent territory would flip (enabled), we avoid it unless it's the target-adjacent capture
        if (nx, ny) in opp_terr:
            score -= 30
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]