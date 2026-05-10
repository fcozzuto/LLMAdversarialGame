def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Deterministic fallback: head toward center while staying away from edges
        cx, cy = w // 2, h // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            v = -dist8(nx, ny, cx, cy) + 0.1 * (dist8(nx, ny, ox, oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick the resource that we can improve our lead on most (opponent nearest-resource style)
    best_r = resources[0]
    best_adv = -10**18
    for rx, ry in resources:
        self_d = dist8(sx, sy, rx, ry)
        opp_d = dist8(ox, oy, rx, ry)
        adv = opp_d - self_d
        # Prefer resources where we are not clearly behind; tie-break by closeness to opponent's side
        val = adv * 10 - self_d * 0.3 + opp_d * 0.05
        if val > best_adv:
            best_adv = val
            best_r = (rx, ry)

    rx, ry = best_r

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        md = dist8(nx, ny, rx, ry)
        od = dist8(ox, oy, rx, ry)
        adv = od - md  # positive means we are closer than opponent at current turn evaluation

        # If staying still, discourage unless it maintains a lead.
        stay_pen = 1.0 if (dx == 0 and dy == 0) else 0.0

        # Also account for other resources: avoid moving into cells that massively lose all leads.
        backup = -10**18
        for j in range(len(resources)):
            tx, ty = resources[j]
            self_d2 = dist8(nx, ny, tx, ty)
            opp_d2 = dist8(ox, oy, tx, ty)
            backup = max(backup, (opp_d2 - self_d2) * 0.6 - self_d2 * 0.03)

        v = adv * 12 - md * 0.35 + backup - stay_pen * 0.4
        # Small bias to move away from obstacles' immediate neighborhood deterministically
        v -= 0.02 * sum(1 for ax, ay in obstacles if dist8(nx, ny, ax, ay) == 0)

        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]