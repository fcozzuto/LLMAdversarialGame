def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If no visible resources, move to reduce distance to the "leading" corner (where opponent is not)
    if not resources:
        target = (0, 0)
        if (ox + oy) <= (sx + sy):
            target = (w - 1, h - 1)
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            score = -man(nx, ny, target[0], target[1])
            if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return list(best[1] if best else (0, 0))

    # Choose a resource we can "reach first" (opp farther than us), otherwise one that is closest.
    # Score = (opp_dist - self_dist) with mild bias to nearer resources and to safer movement.
    best_move = (-(10**9), (0, 0))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Safety/feasibility: small penalty for being adjacent to obstacles (encourages routing around chokepoints)
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if 0 <= xx < w and 0 <= yy < h and (xx, yy) in obstacles:
                    adj_obs += 1

        local_best = -(10**9)
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources where we gain an advantage; if tie, prefer shorter self distance.
            gain = od - sd
            score = 5 * gain - sd - 0.1 * adj_obs
            local_best = score if score > local_best else local_best

        # If many resources exist, encourage progress toward the best candidate by direct movement bias
        # (deterministic tie-breaker already handled).
        if local_best > best_move[0] or (local_best == best_move[0] and (dx, dy) < best_move[1]):
            best_move = (local_best, (dx, dy))

    return [int(best_move[1][0]), int(best_move[1][1])]