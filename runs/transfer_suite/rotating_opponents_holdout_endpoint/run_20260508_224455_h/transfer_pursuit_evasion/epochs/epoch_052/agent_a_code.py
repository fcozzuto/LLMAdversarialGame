def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "evade", "runner", "escape", "coward"))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    adj4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def blocked_penalty(x, y):
        if (x, y) in obstacles:
            return -10_000
        if not is_evader:
            return 0
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    p += 3
        return -p

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        dist = cheb(nx, ny, ox, oy)
        capture_bonus = 2000 if (dist == 0) else 0  # capture ends immediately
        bpen = blocked_penalty(nx, ny)

        if is_evader:
            # Maximize survival: keep far and avoid obstacles; if capture possible, avoid it.
            score = dist * 50 + bpen + capture_bonus
        else:
            # Maximize capture likelihood: move closer, avoid obstacles.
            score = (-dist) * 50 + bpen + capture_bonus

        # Deterministic tie-break: first in fixed move order
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best