def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Blocking-minded: maximize how much closer we can be to at least one resource.
    # Then tie-break by minimizing our distance to that resource.
    best = None  # (val, -min_self_d, dx, dy)
    for dx, dy, nx, ny in candidates:
        min_self_d_for_best = 10**9
        best_adv = -10**9
        for rx, ry in resources:
            self_d = man(nx, ny, 0, 0) + 0  # dummy to keep deterministic int ops
            self_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            adv = opp_d - self_d  # positive means we are closer than opponent
            if adv > best_adv:
                best_adv = adv
                min_self_d_for_best = self_d
            elif adv == best_adv and self_d < min_self_d_for_best:
                min_self_d_for_best = self_d

        # Small bias: prefer moves that also reduce distance to the current best resource.
        # Also lightly discourage moving adjacent to obstacles.
        adj_obs = 0
        for ddx, ddy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            px, py = nx + ddx, ny + ddy
            if 0 <= px < w and 0 <= py < h and (px, py) in obstacles:
                adj_obs += 1

        val = best_adv - 0.05 * adj_obs
        cand = (val, -min_self_d_for_best, dx, dy)
        if best is None or cand > best:
            best = cand

    return [int(best[2]), int(best[3])]