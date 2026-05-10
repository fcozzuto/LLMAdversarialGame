def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    is_evader = ("evad" in self_role) or (("agent" in self_role) and ("evad" in opp_role))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def penalty_adj(nx, ny):
        if not obs:
            return 0.0
        pen = 0.0
        for (x, y) in obs:
            ad = abs(nx - x) + abs(ny - y)
            if ad == 0:
                return 1e9
            if ad == 1:
                pen += 2.5
            elif ad == 2:
                pen += 0.9
        return pen

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in obs:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # Prefer stepping to reduce/increase distance while "cutting" toward a line through the opponent.
    best = None
    best_score = None
    for dx, dy, nx, ny in candidates:
        d = dist2(nx, ny, ox, oy)
        line_dx = 0 if sx == ox else (1 if ox > sx else -1)
        line_dy = 0 if sy == oy else (1 if oy > sy else -1)

        # Alignment/cutoff term: how much the move progresses toward the opponent's direction of travel
        # (heuristic for wall-run evaders: keep pressure by staying aligned when direct line is blocked).
        next_on_line = (nx + line_dx, ny + line_dy)
        align = 0.0
        if in_bounds(next_on_line[0], next_on_line[1]):
            align = 1.0 if next_on_line not in obs else 0.0
        adj_pen = penalty_adj(nx, ny)

        # Deterministic tie-break by ordering of dirs already; add tiny dx/dy-based hash-free bias
        bias = 0.001 * (dx * 3 + dy)

        if is_evader:
            score = -d + 0.8 * align - 0.9 * adj_pen + bias
            # maximize score
            if best_score is None or score > best_score:
                best_score, best = score, [dx, dy]
        else:
            score = d - 0.8 * align + 1.1 * adj_pen + bias
            # minimize score
            if best_score is None or score < best_score:
                best_score, best = score, [dx, dy]

    return best