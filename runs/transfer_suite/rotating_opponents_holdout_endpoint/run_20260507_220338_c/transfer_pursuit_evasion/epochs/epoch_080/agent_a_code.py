def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    i_am_evader = not any(k in role_s for k in ("pursuer", "chaser", "catch", "pursuit"))

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx >= dy else dy  # Chebyshev

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    # If close, prioritize breaking line-of-attack (cornering away from opponent).
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), c[0], c[1]))
    corner_focus = (dist(sx, sy) <= 2)

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist(nx, ny)
        if corner_focus:
            dc = max(abs(far_corner[0] - nx), abs(far_corner[1] - ny))
        else:
            dc = 0

        # Evader: maximize distance; Pursuer: minimize distance.
        score = d if i_am_evader else -d
        # Tie-breaker toward/away from far corner depending on role.
        score += (dc if i_am_evader else -dc) * 0.01

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]