def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def clamp_inb(x, y):
        if x < 0 or x >= w or y < 0 or y >= h:
            return False
        if (x, y) in obstacles:
            return False
        return True

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def obstacle_pressure(x, y):
        # Penalize being adjacent to obstacles (reduces getting stuck near walls).
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    cnt += 1
        return cnt

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Fallback: march toward the center-opposite corner if no resources.
    if not resources:
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        best = (0, 0)
        bestv = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not clamp_inb(nx, ny):
                continue
            v = -(abs(nx - tx) + abs(ny - ty)) - 3 * obstacle_pressure(nx, ny)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # New policy: score each move by best "next-step race" vs opponent over all resources,
    # then add obstacle pressure and a mild preference for moving away from opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not clamp_inb(nx, ny):
            continue
        myd0 = abs(nx - ox) + abs(ny - oy)
        # Race score: for the most favorable resource, how much we improve vs opponent.
        race = -10**18
        for r in resources:
            myd = dist((nx, ny), r)
            opd = dist((ox, oy), r)
            # Prefer positions where we are (or become) closer than opponent; tie-break toward more distant resources.
            v = (opd - myd) * 10 - myd - 2 * obstacle_pressure(nx, ny)
            if v > race:
                race = v
        # Also bias toward increasing our distance from opponent to avoid being out-positioned.
        val = race + 0.6 * myd0 - 0.4 * dist((nx, ny), (sx, sy))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]