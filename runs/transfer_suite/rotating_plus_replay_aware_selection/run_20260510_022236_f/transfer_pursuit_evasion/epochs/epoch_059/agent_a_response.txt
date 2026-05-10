def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def obs_penalty(x, y):
        if (x, y) in obs:
            return 1000000
        if not obs:
            return 0
        best = 10**9
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        if best <= 0:
            return 1000000
        if best == 1:
            return 80
        if best == 2:
            return 25
        if best == 3:
            return 10
        return 0

    best = None
    best_score = -10**30 if is_evader else 10**30
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        p = obs_penalty(nx, ny)
        if p >= 1000000:
            continue

        d = dist(nx, ny, ox, oy)
        cdist = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)

        if is_evader:
            # Maximize separation; prefer edges/corners if safe.
            score = d * 1.0 - p * 1.0 - 0.01 * cdist
        else:
            # Minimize squared distance to opponent; keep some center bias to avoid being boxed.
            score = -d * 1.0 - p * 1.0 - 0.002 * cdist

        if best is None:
            best = [dx, dy]
            best_score = score
        else:
            if is_evader:
                if score > best_score + 1e-9 or (abs(score - best_score) <= 1e-9 and (dx, dy) < tuple(best)):
                    best = [dx, dy]
                    best_score = score
            else:
                if score < best_score - 1e-9 or (abs(score - best_score) <= 1e-9 and (dx, dy) < tuple(best)):
                    best = [dx, dy]
                    best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]