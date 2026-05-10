def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    self_role = str(observation.get("self_role") or "")
    opp_role = str(observation.get("opponent_role") or "")
    self_evader = "evader" in self_role.lower()
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    cx, cy = w / 2.0, h / 2.0

    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        # wall-running evasion: prefer hugging borders when evader
        wall = min(nx, ny, (w - 1 - nx), (h - 1 - ny))
        wall_pref = (w - 1) / 2.0
        wall_term = (wall_pref - wall) / wall_pref  # larger when closer to wall

        # center control: pursuer prefers center-ish for cutoffs; evader avoids center
        center_term = -dist2(nx, ny, cx, cy) / (w * h)

        # obstacle proximity (soft): penalize moves adjacent to obstacles to avoid getting funneled badly
        prox = 0
        for ox2, oy2 in blocked:
            if abs(nx - ox2) + abs(ny - oy2) == 1:
                prox -= 1
        prox *= 0.25

        # pursuer tries to reduce distance; evader tries to increase it
        if self_evader:
            s = d + 2.2 * wall_term - 0.7 * center_term + prox
        else:
            s = -d + 0.9 * center_term + (-0.3 * wall_term) + prox

        # deterministic tie-break: lexicographic smallest move among equals
        if best is None or s > best_score or (s == best_score and (dx, dy) < best):
            best_score = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]