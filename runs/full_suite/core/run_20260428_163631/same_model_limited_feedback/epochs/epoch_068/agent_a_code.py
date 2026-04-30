def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    opp = (ox, oy)
    if not resources:
        # no resources: move to reduce distance to opponent's side (deterministic)
        tx = 0 if sx > w // 2 else w - 1
        ty = 0 if sy > h // 2 else h - 1
        tx, ty = (tx, ty)
        best = min(valid, key=lambda d: dist((sx + d[0], sy + d[1]), (tx, ty)))
        return [int(best[0]), int(best[1])]

    best_score = None
    best_t = None
    for rx, ry in resources:
        r = (rx, ry)
        if r in obstacles:
            continue
        myd = dist(me, r)
        opd = dist(opp, r)
        # Prefer resources closer to me; if opponent is likely closer, penalize.
        score = myd - 0.85 * opd
        # Mild bias to go upward-left first (deterministic tie-break via score then coordinates)
        score += 0.001 * (rx + ry)
        if best_score is None or score < best_score:
            best_score, best_t = score, r

    tx, ty = best_t
    # Prefer steps that reduce my distance to target; penalize moving away.
    def step_score(d):
        nx, ny = sx + d[0], sy + d[1]
        myd = dist((nx, ny), (tx, ty))
        opd = dist((ox, oy), (tx, ty))
        return (myd, -d[0], -d[1], myd + 0.2 * (opd == 0))

    chosen = min(valid, key=step_score)
    return [int(chosen[0]), int(chosen[1])]