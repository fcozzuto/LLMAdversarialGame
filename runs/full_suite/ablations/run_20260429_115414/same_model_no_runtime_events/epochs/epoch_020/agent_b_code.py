def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def score_cell(x, y):
        if (x, y) in obs:
            return -10**9
        # Prefer moving toward a resource where we are relatively closer than opponent.
        best_adv = -10**18
        best_my_d = 10**9
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            myd = abs(rx - x) + abs(ry - y)
            opd = abs(rx - ox) + abs(ry - oy)
            adv = opd - myd  # positive is good (we are closer)
            if adv > best_adv or (adv == best_adv and myd < best_my_d):
                best_adv = adv
                best_my_d = myd
        if resources:
            # Also softly prefer being closer overall to reduce worst-case
            # and slightly prefer not increasing opponent distance.
            base = best_adv * 100 - best_my_d
        else:
            base = (abs(ox - x) + abs(oy - y)) * -1
        # Discourage stepping into squares adjacent to obstacles (path friction).
        adj = 0
        for dx, dy in candidates:
            nx = x + dx; ny = y + dy
            if (nx, ny) in obs:
                adj += 1
        return base - 2 * adj

    # If no resources, drift to center-ish while keeping away from obstacles.
    if not resources:
        target = (w // 2, h // 2)
        best = (0, 0); bestv = -10**18
        tx, ty = target
        for dx, dy in candidates:
            nx = sx + dx; ny = sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            v = -(abs(tx - nx) + abs(ty - ny))
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in candidates:
        nx = sx + dx; ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        v = score_cell(nx, ny)

        # Deterministic tie-breaks: keep move with highest value, then smallest my distance to best target
        # approximated by negative value already; further tie by lexicographic (dx,dy).
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
        elif v == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]