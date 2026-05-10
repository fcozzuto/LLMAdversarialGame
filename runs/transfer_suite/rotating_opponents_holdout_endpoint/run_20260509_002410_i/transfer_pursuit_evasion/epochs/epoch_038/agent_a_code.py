def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    is_evader = (self_role == "evader") or (opponent_role == "pursuer") or ("evader" in self_role)
    is_pursuer = (self_role == "pursuer") or (opponent_role == "evader") or ("pursuer" in self_role)

    # 8-neighbors + stay
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Prefer determinism: fixed tie-break order via list order.

    best = None
    best_score = None

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Evader: maximize distance from pursuer while avoiding obstacles.
    # Pursuer: minimize distance to evader while avoiding obstacles.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d2 = dist2(nx, ny, ox, oy)

        # Wall-running tendency: keep moving away/toward in Manhattan sense too.
        man = abs(nx - ox) + abs(ny - oy)
        step_toward_corner = 0
        # If evader, bias toward farthest corner; if pursuer, toward nearest corner.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        if is_evader:
            # choose farthest corner from opponent
            # (deterministic: iterate fixed corner list)
            far = corners[0]
            farv = dist2(far[0], far[1], ox, oy)
            for c in corners[1:]:
                v = dist2(c[0], c[1], ox, oy)
                if v > farv:
                    far, farv = c, v
            step_toward_corner = -dist2(nx, ny, far[0], far[1])  # closer to farthest-corner target
        elif is_pursuer:
            near = corners[0]
            nearv = dist2(near[0], near[1], ox, oy)
            for c in corners[1:]:
                v = dist2(c[0], c[1], ox, oy)
                if v < nearv:
                    near, nearv = c, v
            step_toward_corner = -dist2(nx, ny, near[0], near[1])

        if is_evader and not is_pursuer:
            # Maximize: farther from opponent + slight corner bias
            score = d2 + 0.1 * man + 0.01 * step_toward_corner
            if best_score is None or score > best_score:
                best_score = score
                best = [dx, dy]
        else:
            # Default to pursuer chase if not clearly evader
            score = -d2 - 0.1 * man + 0.01 * step_toward_corner
            if best_score is None or score > best_score:
                best_score = score
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]