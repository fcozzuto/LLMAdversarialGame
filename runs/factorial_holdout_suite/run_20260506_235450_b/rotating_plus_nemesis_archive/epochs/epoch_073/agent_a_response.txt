def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obs.add((px, py))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                res.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def md(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not res:
        # Deterministic fallback: drift toward nearest corner away from opponent
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best_corner = None
        best_val = -10**18
        for c in corners:
            if c in obs:
                continue
            val = md((sx, sy), (ox, oy)) - md((sx, sy), c)
            if val > best_val:
                best_val = val
                best_corner = c
        tx, ty = best_corner if best_corner else (w - 1, h - 1)
        bx = 0; by = 0
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                d = md((nx, ny), (tx, ty))
                if d < md((sx, sy), (tx, ty)):
                    bx, by = dx, dy
                    break
        return [bx, by]

    # Greedy-denier-aware 1-step evaluation
    opp_dist_here = md((sx, sy), (ox, oy))
    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Prefer collecting: if adjacent/at resource, strong bonus via min distance
        my_d = 10**9
        opp_d = 10**9
        for (rx, ry) in res:
            d1 = md((nx, ny), (rx, ry))
            if d1 < my_d:
                my_d = d1
            d2 = md((ox, oy), (rx, ry))
            if d2 < opp_d:
                opp_d = d2

        # Choose resources where we can "arrive first" or at least improve relative advantage
        rel = (opp_d - my_d)
        score = 0
        score += 3.0 / (1 + my_d)          # collection pressure
        score += 0.25 * rel               # denier pressure
        score += 0.05 * (opp_dist_here - md((nx, ny), (ox, oy)))  # keep distance if possible

        # Tie-break: deterministic move ordering preference (center-ish towards resources)
        if score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    return best_move