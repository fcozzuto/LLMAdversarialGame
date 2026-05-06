def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def d(a, b):
        # Chebyshev distance matches allowed diagonal steps
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        # Deterministic drift toward center to reduce passivity
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            k = (d((nx, ny), (tx, ty)), dx, dy)
            if best is None or k < best[0]:
                best = (k, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    aggressive = 1 if rem <= 6 else 0

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Denial-oriented evaluation: prefer states where we are closer than opponent,
        # and especially where we can contest opponent's likely target.
        best_res = None
        for rx, ry in resources:
            self_d = d((nx, ny), (rx, ry))
            opp_d = d((ox, oy), (rx, ry))

            # Positive when we are advancing relative to opponent on that resource.
            rel = opp_d - self_d

            # Slight preference for near resources; stronger when aggressive/late-game.
            near = self_d
            # If opponent can reach sooner, penalize, but still allow blocking moves.
            contest_pen = 2 * (1 if opp_d < self_d else 0)

            val = (-rel, near + contest_pen - (aggressive * min(rel, 2)))
            if best_res is None or val < best_res:
                best_res = val

        # Break ties deterministically by move order
        k = (best_res, dx, dy)
        if best is None or k < best[0]:
            best = (k, dx, dy)

    return [best[1], best[2]] if best else [0, 0]