def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("hunter" in role) or ("chaser" in role)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    capture_radius = int(observation.get("capture_radius", 0) or 0)

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue

        d = cheb(nx, ny, ox, oy)
        is_capture = (d <= capture_radius)

        # Obstacle avoidance: slight penalty near blocked cells.
        near_block = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in blocked:
                    near_block += 1

        # 1-step policy: pursuer minimizes distance (and prefers capture), evader maximizes distance.
        # Deterministic tie-break uses tuple ordering.
        if pursuer:
            score = (-1000000 if is_capture else 0) + (d * 1000) + near_block
            key = (0 if is_capture else 1, score, nx, ny, dx, dy)
            better = (best_score is None) or (key < best_score)
        else:
            score = (1000000 if is_capture else 0) + (-d * 1000) - near_block
            key = (0 if not is_capture else 1, score, nx, ny, dx, dy)
            better = (best_score is None) or (key < best_score)

        if better:
            best_score = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best