def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    self_is_pursuer = any(k in sr for k in ("pursuer", "chaser", "seeker", "hunter"))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Predict evader's likely corner: farthest from our current position.
    target_corner = max(corners, key=lambda c: d2(sx, sy, c[0], c[1]))
    tx, ty = target_corner

    best_move = [0, 0]
    if self_is_pursuer:
        best_score = None  # lower is better
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            dist_opp = d2(nx, ny, ox, oy)
            dist_corner = d2(nx, ny, tx, ty)
            score = dist_opp * 3 + dist_corner  # intercept while keeping close
            if best_score is None or score < best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
                best_score = score
                best_move = [dx, dy]
    else:
        best_score = None  # higher is better
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            dist_opp = d2(nx, ny, ox, oy)
            dist_corner = d2(nx, ny, tx, ty)
            # If we're evader, go toward the corner while maximizing distance.
            score = dist_opp * 3 + dist_corner
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]