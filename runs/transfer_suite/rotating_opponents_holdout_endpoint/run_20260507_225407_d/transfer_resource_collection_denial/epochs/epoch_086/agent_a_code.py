def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    # Prefer racing early, denial later.
    race_weight = 1.0 if rem > 6 else 1.2
    deny_weight = 0.2 if rem > 6 else 0.8

    # Pick best resource deterministically using a score combining:
    # (closer to me) - (closer to opponent) + obstacle proximity penalty.
    best_t = resources[0]
    best_score = None
    for tx, ty in resources:
        d_me = dist(sx, sy, tx, ty)
        d_op = dist(ox, oy, tx, ty)
        obs_pen = 0
        for ax, ay in obstacles:
            dd = abs(tx - ax) + abs(ty - ay)
            if dd == 0:
                obs_pen += 1000
            elif dd == 1:
                obs_pen += 6
            elif dd == 2:
                obs_pen += 2
        score = race_weight * d_me - deny_weight * (d_op - d_me) + obs_pen
        if best_score is None or score < best_score or (score == best_score and (tx, ty) < best_t):
            best_score = score
            best_t = (tx, ty)

    tx, ty = best_t
    dx_needed = 0 if tx == sx else (1 if tx > sx else -1)
    dy_needed = 0 if ty == sy else (1 if ty > sy else -1)

    # Evaluate all legal one-step deltas, prefer moving toward target but avoid obstacle cells.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = moves[4]
    best_m_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Avoid stepping near obstacles slightly.
        obs_pen = 0
        for ax, ay in obstacles:
            ddx, ddy = abs(nx - ax), abs(ny - ay)
            if ddx == 0 and ddy == 0:
                obs_pen += 1000
            elif max(ddx, ddy) <= 1:
                obs_pen += 4
            elif ddx + ddy == 2:
                obs_pen += 1

        d_me = dist(nx, ny, tx, ty)
        d_op = dist(nx, ny, ox, oy)
        toward = - (abs(dx_needed - dx) + abs(dy_needed - dy))
        # Also keep some spacing from opponent (shadow archetype can exploit contact).
        score = d_me + obs_pen + 0.15 * d_op + 0.4 * (abs(nx - ox) + abs(ny - oy)) + 0.1 * (-toward)
        if best_m_score is None or score < best_m_score or (score == best_m_score and (dx, dy) < best_m):
            best_m_score = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]