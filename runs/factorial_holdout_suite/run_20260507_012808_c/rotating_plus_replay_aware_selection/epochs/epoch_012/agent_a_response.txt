def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    # If no resources visible, head toward the more promising corner (farthest-sum tie-break).
    if not resources:
        cand = [((0, 0), (sx + sy)), ((w - 1, h - 1), (w - 1 - sx) + (h - 1 - sy)),
                ((w - 1, 0), (w - 1 - sx) + sy), ((0, h - 1), sx + (h - 1 - sy))]
        target = min(cand, key=lambda t: t[1])[0]
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            k = dist((nx, ny), target)
            if best is None or k < best[0]:
                best = (k, dx, dy)
        return [best[1], best[2]]

    # Prefer moves that secure a resource where we are closer than the opponent.
    # Evaluate each neighbor position by its best achievable resource advantage.
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy

        # Resource advantage: positive means we are closer than opponent.
        best_adv = None
        best_t = None
        for rx, ry in resources:
            sd = dist((nx, ny), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            adv = od - sd
            # Tie-break: smaller self distance, then smaller resource coords for determinism.
            key = (adv, -sd, -(rx * 100 + ry))
            if best_adv is None or key > best_adv:
                best_adv = key
                best_t = (rx, ry)

        adv = best_adv[0]
        sd = dist((nx, ny), best_t)
        od = dist((ox, oy), best_t)

        # If all advantages are negative, race nearest to prevent dithering.
        # Overall score: maximize advantage, then minimize our distance; mild penalty for getting worse vs current.
        cur_best = None
        for rx, ry in resources:
            sd0 = dist((sx, sy), (rx, ry))
            od0 = dist((ox, oy), (rx, ry))
            adv0 = od0 - sd0
            key0 = (adv0, -sd0, -(rx * 100 + ry))
            if cur_best is None or key0 > cur_best:
                cur_best = key0
        cur_adv = cur_best[0]

        score = (adv - 0.05 * (sd == od), -sd, -abs(adv - cur_adv), -(best_t[0] * 100 + best_t[1]))
        if best_move is None or score > best_move[0]:
            best_move = (score, dx, dy)

    return [int(best_move[1]), int(best_move[2])]