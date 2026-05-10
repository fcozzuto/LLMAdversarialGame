def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in sr) or ("runner" in sr) or ("evasion" in sr)
    if ("pursuer" in sr) or ("chaser" in sr) or ("hunter" in sr):
        is_evader = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def min_obst_dist2(x, y):
        md = None
        for (ax, ay) in obstacles:
            d = dist2(x, y, ax, ay)
            if md is None or d < md:
                md = d
        return 999999 if md is None else md

    best = None
    best_score = None
    # Deterministic tie-break by preferring earlier move in fixed order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d2 = dist2(nx, ny, ox, oy)
        if is_evader:
            # Maximize separation; keep away from obstacles and avoid moving into tighter areas.
            score = d2 + 0.01 * min_obst_dist2(nx, ny) + 0.001 * (abs(nx - ox) + abs(ny - oy))
        else:
            # Pursue: minimize separation; also lightly prefer moves that align toward opponent.
            score = -d2 + 0.001 * (nx - sx) * (ox - sx) + 0.001 * (ny - sy) * (oy - sy)
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best