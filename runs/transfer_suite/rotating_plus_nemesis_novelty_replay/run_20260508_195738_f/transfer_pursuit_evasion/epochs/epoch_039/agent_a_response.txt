def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    self_role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in self_role) or ("chaser" in self_role) or ("tagger" in self_role)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # BFS shortest path length with 8-direction movement; deterministic via fixed neighbor order.
    def dist_path(a, b):
        ax, ay = a
        bx, by = b
        if (ax, ay) == (bx, by):
            return 0
        if not ok(ax, ay) or not ok(bx, by):
            return 10**6
        qx, qy = [ax], [ay]
        head = 0
        seen = {(ax, ay)}
        steps = 0
        while head < len(qx) and steps <= 20:
            steps += 1
            nq = len(qx)
            while head < nq:
                x, y = qx[head], qy[head]
                head += 1
                if (x, y) == (bx, by):
                    return steps - 1
                for dx, dy in moves:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) not in seen and ok(nx, ny):
                        seen.add((nx, ny))
                        qx.append(nx)
                        qy.append(ny)
            # loop repeats
        return 10**6

    best = None
    best_val = None
    # Tie-break deterministically by move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if nx == ox and ny == oy:
            val = -10**9 if pursuer else 10**9  # pursuer prefers immediate capture, evader avoids
        else:
            d = dist_path((nx, ny), (ox, oy))
            # Prefer moving to shorten/lengthen path distance; add small direct-distance bias.
            direct = max(abs(nx - ox), abs(ny - oy))
            if pursuer:
                val = -(d * 100 + direct)
            else:
                val = d * 100 + direct
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [best[0], best[1]]