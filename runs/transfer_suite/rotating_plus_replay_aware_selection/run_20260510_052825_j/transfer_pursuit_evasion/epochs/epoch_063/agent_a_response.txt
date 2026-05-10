def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evad" in self_role) or (self_role == "evader") or ("purs" in opponent_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if self_is_evader:
        tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        goal = (tx, ty)
    else:
        goal = (ox, oy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_goal = dist2(nx, ny, goal[0], goal[1])

        # Heuristic:
        # - Evader: maximize distance to pursuer; also prefer moving toward "escape corner".
        # - Pursuer: minimize distance to evader; also prefer moving toward opponent position.
        if self_is_evader:
            score = (d_opp * 1000) - d_goal
        else:
            score = (-d_opp * 1000) - d_goal

        # Deterministic tie-breaker: prefer earlier moves order and staying still last.
        tie = best_score == score
        if best_score is None or score > best_score or (tie and (dx, dy) == best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]