def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def step_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # deterministic drift to center-ish
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    best_target = resources[0]
    best_score = -10**30
    for rx, ry in resources:
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; discourage long travel.
        # Also favor eliminating contest where opponent is farther.
        score = (opd - myd) * 1000 - myd * 3 - opd
        # Deterministic tie-break: closer to my position if score ties, then lexicographic
        if score > best_score:
            best_score = score
            best_target = (rx, ry)
        elif score == best_score:
            if myd < manh(sx, sy, best_target[0], best_target[1]):
                best_target = (rx, ry)
            elif myd == manh(sx, sy, best_target[0], best_target[1]):
                if (rx, ry) < best_target:
                    best_target = (rx, ry)

    rx, ry = best_target
    best_move = (0, 0)
    best_mv_score = -10**30
    cur_myd = manh(sx, sy, rx, ry)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny):
            continue
        myd = manh(nx, ny, rx, ry)
        # after-step opponent advantage estimate (static opponent position)
        opd = manh(ox, oy, rx, ry)
        adv = opd - myd
        # primary: reduce distance; secondary: increase advantage; tertiary: keep stable
        mv_score = adv * 1000 - myd * 4
        # encourage progress if stuck
        if dx == 0 and dy == 0 and myd == cur_myd:
            mv_score -= 50
        if mv_score > best_mv_score:
            best_mv_score = mv_score
            best_move = (dx, dy)
        elif mv_score == best_mv_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]