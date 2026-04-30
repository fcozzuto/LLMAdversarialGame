def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
                  (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources:
        # Drift toward center to avoid corner traps when no resources known.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestd = 10**9
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, cx, cy)
            if d < bestd:
                bestd = d
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_val = -10**18
    best_tiebreak = 10**18

    # Deterministic iteration order: candidates as given.
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_best = -10**18
        # Interception/priority: maximize advantage on the best available resource.
        # Slightly favor moves that get us closer to our top resource.
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)

            # If we can reach immediately, strongly prefer.
            reach_bonus = 1000 if md == 0 else (200 if md == 1 else 0)

            # Core advantage: how much closer we are than opponent.
            val = (od - md) + reach_bonus

            # If opponent is extremely close to the resource, favor blocking-like proximity.
            if od <= 1 and md <= 2:
                val += 50 - 10 * md

            if val > my_best:
                my_best = val

        # Prefer higher value, then smaller my distance to the best "target" for stability.
        # Use the best single-resource based on same metric for tie-break.
        tdist = 10**9
        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            val = (od - md)
            if od == 0:
                val += 1000
            if val > my_best - 1e-9:
                if md < tdist:
                    tdist = md

        if my_best > best_val or (my_best == best_val and tdist < best_tiebreak):
            best_val = my_best
            best_tiebreak = tdist
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]