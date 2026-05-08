def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    evader = any(k in role for k in ("evader", "escape", "runner", "flee", "evade"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Candidate evaluation: pursuer minimizes dist; evader maximizes dist.
    # Secondary: prefer safer positions (more free neighbors) and reduce being pushed into corners.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy) if evader else -dist2(c[0], c[1], ox, oy))

    def free_neighbors(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        dcur = dist2(sx, sy, ox, oy)
        dnew = dist2(nx, ny, ox, oy)
        dd = dnew - dcur

        # Primary objective
        primary = (-dnew) if not evader else (dnew)

        # Secondary objectives
        fn = free_neighbors(nx, ny)
        corner_dist = dist2(nx, ny, target_corner[0], target_corner[1])

        # Weighting: favor escape/approach first, then safety, then corner bias
        score = primary * 1000 + fn * 10 + (-corner_dist if evader else corner_dist * -0.01)

        # If evader, avoid moves that drastically reduce distance; if pursuer, avoid moves that drastically increase distance
        if evader and dd < -4:
            score -= 50
        if (not evader) and dd > 4:
            score -= 50

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]