def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        if (sx, sy) not in obstacles:
            return [0, 0]
        # If somehow trapped, pick any safe move
        for m in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = sx + m[0], sy + m[1]
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [m[0], m[1]]
        return [0, 0]

    def cheb(a, b, c, d):
        da = a - c
        if da < 0: da = -da
        db = b - d
        if db < 0: db = -db
        return da if da > db else db

    # Choose best target by advantage over opponent; deterministic tie-breakers.
    best = None
    best_adv = None
    best_sdist = None
    for r in resources:
        rx, ry = r[0], r[1]
        sdist = cheb(sx, sy, rx, ry)
        odist = cheb(ox, oy, rx, ry)
        adv = odist - sdist
        if best is None or adv > best_adv or (adv == best_adv and (sdist < best_sdist or (sdist == best_sdist and (rx < best[0] or (rx == best[0] and ry < best[1]))))):
            best = (rx, ry)
            best_adv = adv
            best_sdist = sdist

    tx, ty = best
    # Evaluate moves toward target, avoid obstacles, add slight preference away from opponent if equal.
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        tdist = cheb(nx, ny, tx, ty)
        odist = cheb(nx, ny, ox, oy)
        # Primary: reduce distance to target; Secondary: keep distance from opponent; Tertiary: prefer progress (prefer diagonal/forward implicitly).
        score = (tdist, -odist, -(abs(dx) + abs(dy)))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    nx, ny = sx + dx, sy + dy
    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
        return [dx, dy]
    return [0, 0]