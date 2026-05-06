def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            obstacles.add((px, py))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def manh(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    # Predict opponent's likely target: nearest resource to opponent.
    opp_target = None
    best_od = 10**9
    for rx, ry in resources:
        od = manh(ox, oy, rx, ry)
        if od < best_od or (od == best_od and (rx, ry) < opp_target):
            best_od = od
            opp_target = (rx, ry)

    rt_x, rt_y = opp_target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        my_d = manh(nx, ny, rt_x, rt_y)
        my_now = manh(sx, sy, rt_x, rt_y)

        opp_d = manh(ox, oy, rt_x, rt_y)
        # Intercept: improve relative position vs opponent on opponent's target.
        score = (opp_d - my_d) * 3.0

        # Encourage progress on the target.
        score += (my_now - my_d) * 1.2

        # Discourage getting too close (safe_collector tends to avoid contact; we still avoid being trapped).
        score -= manh(nx, ny, ox, oy) * 0.08

        # If we would land on another resource, add a small deterministic bonus.
        if (nx, ny) in resources:
            score += 4.0

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]