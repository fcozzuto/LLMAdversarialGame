def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "evade", "runner", "escape", "coward"))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    t = int(observation.get("turn_index", 0) or 0)
    # Alternate target-corner bias to avoid getting predictable.
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    corner_bias = far_corner if (t % 2 == 0) else near_corner

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            nx, ny = sx, sy
        if (nx, ny) in obs:
            nx, ny = sx, sy  # engine would keep in place anyway

        d = cheb(nx, ny, ox, oy)
        corner_d = cheb(nx, ny, corner_bias[0], corner_bias[1])

        # Primary objective: distance to opponent.
        # Evader: maximize distance; Pursuer: minimize distance.
        primary = d if is_evader else -d

        # Secondary: move toward/away from corner bias deterministically.
        # Evader prefers far from opponent and away from near_corner/into far_corner;
        # Pursuer prefers approach opponent and slight corner-chasing to restrict escape.
        secondary = corner_d if is_evader else -corner_d

        # Light wall/obstacle penalty if the move would collide.
        collided = ((sx + dx, sy + dy) in obs) or (sx + dx < 0 or sx + dx >= w or sy + dy < 0 or sy + dy >= h)
        penalty = -5 if collided else 0

        score = primary * 100 + secondary + penalty

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move