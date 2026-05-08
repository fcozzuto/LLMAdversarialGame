def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    evader = ("evader" in role) and ("pursuer" not in role)
    if "pursuer" in role:
        evader = False

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def center_score(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dx = x - cx
        if dx < 0:
            dx = -dx
        dy = y - cy
        if dy < 0:
            dy = -dy
        d2 = dx * dx + dy * dy
        return d2

    best_val = None
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d = cheb(nx, ny, ox, oy)

        # Heuristic: main objective is distance to opponent.
        # For tie-breaking, evader prefers staying away from walls/obstacles by drifting toward center.
        # For pursuer, tie-break prefers diagonal moves (faster capture geometry).
        diag_bonus = 0 if (dx == 0 or dy == 0) else 0.001
        if evader:
            # Maximize: distance, then center proximity (smaller center_score), then diagonal
            val = (d, -center_score(nx, ny), diag_bonus)
        else:
            # Minimize: distance, then prefer diagonal
            val = (-d, diag_bonus, -center_score(nx, ny))

        if best_val is None:
            best_val = val
            best_move = (dx, dy)
        else:
            if evader:
                if val > best_val:
                    best_val = val
                    best_move = (dx, dy)
            else:
                if val > best_val:
                    best_val = val
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]