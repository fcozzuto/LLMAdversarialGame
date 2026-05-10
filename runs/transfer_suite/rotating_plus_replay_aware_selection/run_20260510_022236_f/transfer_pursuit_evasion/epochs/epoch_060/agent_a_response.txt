def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obs = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obs_pen(x, y):
        if not obs_set:
            return 0
        best = 10**9
        for ax, ay in obs_set:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        if best == 0:
            return 10**6
        if best == 1:
            return 200
        if best == 2:
            return 40
        if best == 3:
            return 10
        return 0

    best = None
    best_score = -10**18 if is_evader else 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue

        d_now = dist(sx, sy, ox, oy)
        d_new = dist(nx, ny, ox, oy)

        # Evader: maximize separation; Pursuer: minimize separation.
        if is_evader:
            score = 1000 * (d_new - d_now) + 0.5 * d_new - obs_pen(nx, ny)
        else:
            score = -1000 * (d_new - d_now) - 0.5 * d_new - obs_pen(nx, ny)

        # Deterministic tie-break: prefer moves that keep you in the same general quadrant
        # relative to opponent; then prefer staying still over later lexicographic moves.
        tie = (abs(nx - sx) + abs(ny - sy), 0 if (dx == 0 and dy == 0) else 1, dx, dy)
        if is_evader:
            if score > best_score or (score == best_score and best is not None and tie < best[0]):
                best_score = score
                best = (tie, [dx, dy])
        else:
            if score < best_score or (score == best_score and best is not None and tie < best[0]):
                best_score = score
                best = (tie, [dx, dy])

    return best[1] if best is not None else [0, 0]