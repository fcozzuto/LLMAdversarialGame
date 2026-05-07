def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    def best_candidate():
        if resources:
            # Choose resource where we are relatively closer than opponent
            best_key = None
            best_move = (0, 0)
            for mx, my in moves:
                nx, ny = sx + mx, sy + my
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                # Evaluate next position against each available resource
                local_best = None
                for rx, ry in resources:
                    myd = dist2(nx, ny, rx, ry)
                    opd = dist2(ox, oy, rx, ry)
                    # Prefer moving toward resources we can win; slight tie-break by absolute progress
                    key = (myd - (opd * 9) // 10, myd + opd, rx, ry)
                    if local_best is None or key < local_best:
                        local_best = key
                if local_best is None:
                    continue
                # Prefer smaller key overall; slight preference for moving without staying
                stay_pen = 1 if (mx == 0 and my == 0) else 0
                key2 = (local_best[0], local_best[1], stay_pen, nx, ny)
                if best_key is None or key2 < best_key:
                    best_key = key2
                    best_move = (mx, my)
            return list(best_move)

        # No resources: head to a nearest corner (deterministic)
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda p: dist2(sx, sy, p[0], p[1]))
        best_key = None
        best_move = (0, 0)
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            key = (dist2(nx, ny, tx, ty), abs(nx - ox) + abs(ny - oy), nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (mx, my)
        return list(best_move)

    return best_candidate()