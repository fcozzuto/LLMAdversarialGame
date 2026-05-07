def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
    res_set = set(resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    best_move = (0, 0)
    best_score = -10**30

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # If we can collect now, strongly prioritize.
        if (nx, ny) in res_set:
            score = 10**18 + 1000 * (man((nx, ny), (ox, oy)) == 1) - (nx + ny)
        else:
            # One-step lookahead: choose the best remaining resource from the next position.
            score = -10**30
            for rx, ry in resources:
                sd = abs(rx - nx) + abs(ry - ny)
                od = abs(rx - ox) + abs(ry - oy)
                # Prefer resources we are closer to than opponent; tie-break by closeness and position.
                margin = od - sd
                val = (margin * 10_000) - sd * 10 + (rx * 3 - ry * 2)
                # Bias toward resources likely reachable quickly.
                if margin < 0:
                    val -= 50_000
                if val > score:
                    score = val
            # Additional shaping: reduce our distance to the best resource from current.
            # (cheap proxy without full recomputation)
            cur_best = -10**30
            for rx, ry in resources:
                sd0 = abs(rx - sx) + abs(ry - sy)
                od0 = abs(rx - ox) + abs(ry - oy)
                m0 = od0 - sd0
                v0 = (m0 * 10_000) - sd0 * 10
                if m0 < 0:
                    v0 -= 50_000
                if v0 > cur_best:
                    cur_best = v0
            # Prefer moves that improve the proxy.
            score += (cur_best - score) * 0  # deterministic no-op, keeps stability

        # Deterministic tie-break: fixed order by (dx,dy) plus prefer smaller lexicographic movement.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]