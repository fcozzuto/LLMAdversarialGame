def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    self_is_evader = ("evader" in self_role) and ("pursuer" not in self_role)
    self_is_pursuer = ("pursuer" in self_role) and ("evader" not in self_role)
    if not (self_is_evader or self_is_pursuer):
        self_is_evader = ("evader" in opponent_role) and ("pursuer" not in opponent_role)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]
    best_score = -10**18 if self_is_evader else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue

        dist = max(abs(nx - ox), abs(ny - oy))  # Chebyshev (good for capture at radius 0 with diag moves)
        edge = min(nx, ny, (w - 1 - nx), (h - 1 - ny))  # farther from walls is safer for evasion
        # Obstacle adjacency penalty
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                x2, y2 = nx + ax, ny + ay
                if inside(x2, y2) and (x2, y2) in blocked:
                    adj += 1

        # Small preference to keep moving on evasion to defeat zigzag patterns
        mov = 0 if (dx == 0 and dy == 0) else 1

        if self_is_evader:
            score = dist * 12 + edge * 2 + mov * 0.5 - adj * 3
            if score > best_score:
                best_score = score
                best = [dx, dy]
        else:
            score = dist * 12 - edge * 0.5 + adj * 2  # minimize dist; slight avoid walls/adj obstacles
            if score < best_score:
                best_score = score
                best = [dx, dy]

    return [int(best[0]), int(best[1])]