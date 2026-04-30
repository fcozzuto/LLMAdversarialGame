def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    resources = observation["resources"]
    # If standing on a resource, stay to secure it
    if (sx, sy) in set((x, y) for x, y in resources):
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp = (ox, oy)
    best = None
    best_score = -10**18
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist(opp, (rx, ry))
        # Prefer resources where we're closer; add slight bias to reduce absolute distance
        score = (od - sd) * 10 - sd
        # If tied, bias toward higher x then y to be deterministic
        score += (rx * 0.001) + (ry * 0.000001)
        if score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best if best is not None else (sx, sy)

    def step_toward(cx, cy, tx, ty):
        dx = 0 if tx == cx else (1 if tx > cx else -1)
        dy = 0 if ty == cy else (1 if ty > cy else -1)
        return dx, dy

    # Candidate moves (all legal deltas)
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy))
    if not candidates:
        return [0, 0]

    desired = step_toward(sx, sy, tx, ty)
    # Evaluate candidates: minimize distance to target, maximize being closer than opponent to target, then deterministic tie-break
    bestd = None
    bestv = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        sd = dist((nx, ny), (tx, ty))
        od = dist(opp, (tx, ty))
        v = (od - sd) * 10 - sd
        # Prefer desired move slightly; deterministic tie-break by dx,dy
        if (dx, dy) == desired:
            v += 1.0
        v += dx * 1e-6 + dy * 1e-7
        if v > bestv:
            bestv = v
            bestd = (dx, dy)
    return [int(bestd[0]), int(bestd[1])]