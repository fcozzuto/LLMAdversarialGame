def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def manhmax(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = manhmax(sx, sy, rx, ry)
            od = manhmax(ox, oy, rx, ry)
            # Prefer targets we can reach no later; break ties by my smaller distance then coords.
            key = (0 if sd <= od else 1, sd - od, sd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best if best is not None else (w // 2, h // 2)

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    bestm = (0, 0)
    bestv = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Value: prefer moves that reduce distance to target and keep ahead of opponent.
        myd = manhmax(nx, ny, tx, ty)
        opd = manhmax(ox, oy, tx, ty)
        reach_adv = myd - opd
        # Deterministic tie-breakers: prefer diagonal/straight toward target, then lexicographic delta.
        toward = (1 if (nx - sx) == (1 if tx > sx else -1 if tx < sx else 0) else 0) + (1 if (ny - sy) == (1 if ty > sy else -1 if ty < sy else 0) else 0)
        val = (reach_adv, myd, -toward, dx, dy)
        if bestv is None or val < bestv:
            bestv = val
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]