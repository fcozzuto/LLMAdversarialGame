def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        # No resources: drift toward center while not suicidally close to opponent.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        bestd, bestv = (0, 0), -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dcen = man(nx, ny, cx, cy)
            dop = man(nx, ny, ox, oy)
            v = -0.7 * dcen + 0.9 * (2 - dop if dop <= 2 else 0) - 0.01 * (nx + ny)
            if v > bestv:
                bestv, bestd = v, (dx, dy)
        return [bestd[0], bestd[1]]

    # Pick a deterministic "best" target by racing: closer to self than opponent.
    best_res, best_key = None, None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        key = (ds - 0.6 * do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)
    if best_res is None:
        return [0, 0]
    tx, ty = best_res

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestd, bestv = (0, 0), -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dcur = man(nx, ny, tx, ty)
        dopp = man(nx, ny, ox, oy)
        # Prefer stepping onto/near target, keep some distance from opponent when very close,
        # and add mild obstacle-adjacency penalty.
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    adj_obs += 1
        v = -1.8 * dcur + (2.2 if dcur == 0 else 0.0) + (1.0 if dcur <= 1 else 0.0)
        v += 0.7 * (3 - dcur if dcur <= 3 else 0)  # keep pressure early
        v += (-1.2 * (3 - dopp) if dopp <= 3 else 0)  # avoid being too close
        v += -0.15 * adj_obs
        v += -0.01 * man(nx, ny, (w - 1) // 2, (h - 1) // 2)
        if v > bestv or (v == bestv and (dx, dy) < bestd):
            bestv, bestd = v, (dx, dy)
    return [bestd[0], bestd[1]]