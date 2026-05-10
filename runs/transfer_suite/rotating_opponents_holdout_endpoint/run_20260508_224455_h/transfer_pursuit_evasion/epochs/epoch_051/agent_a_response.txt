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

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def obs_pen(x, y):
        # Prefer avoiding obstacles; also avoid cells adjacent to obstacles when evading.
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    p += 1
        if (x, y) in obstacles:
            p += 10
        return p

    # Tie-break deterministically by move order.
    best_move = [0, 0]
    if is_evader:
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            dist = cheb(nx, ny, ox, oy)
            edge = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
            # Evade: maximize distance; favor staying near edges while keeping away from obstacles.
            score = dist * 10 - obs_pen(nx, ny) * 3 - edge
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            dist = cheb(nx, ny, ox, oy)
            # Pursue: minimize distance; avoid obstacles; slightly prefer moving toward opponent's side.
            towards = (abs(ox - nx) + abs(oy - ny))
            score = -dist * 10 - obs_pen(nx, ny) * 5 - towards * 0.1
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    # If all candidate moves invalid (surrounded), stay.
    return [int(best_move[0]), int(best_move[1])]