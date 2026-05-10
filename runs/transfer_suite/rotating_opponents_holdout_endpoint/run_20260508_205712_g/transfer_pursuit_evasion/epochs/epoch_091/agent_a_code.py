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

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    # Pursuit: "cut off" by aiming slightly past the opponent along the vector from pursuer to opponent.
    # Evade: maximize distance, but add a "flow" term to avoid moving into constrained areas.
    if not is_evader:
        vx, vy = ox - sx, oy - sy
        tx, ty = ox + (1 if vx > 0 else -1 if vx < 0 else 0), oy + (1 if vy > 0 else -1 if vy < 0 else 0)
        if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obstacles:
            tx, ty = ox, oy
        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_op = dist(nx, ny, ox, oy)
            d_tar = dist(nx, ny, tx, ty)
            # Prefer lower distance to opponent; if tie, prefer being closer to the cutoff target.
            score = d_op * 100 + d_tar
            if best is None or score < best_score:
                best, best_score = (dx, dy), score
        return [best[0], best[1]] if best is not None else [0, 0]
    else:
        # Evade: move toward farthest corner relative to pursuer, penalize tight neighborhoods and stepping adjacent to pursuer.
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        cx, cy = max(corners, key=lambda p: dist(p[0], p[1], ox, oy))
        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_far = dist(nx, ny, cx, cy)
            d_op = dist(nx, ny, ox, oy)
            # Neighborhood openness
            open_cnt = 0
            for adx, ady in moves:
                ax, ay = nx + adx, ny + ady
                if valid(ax, ay):
                    open_cnt += 1
            # Penalize being adjacent to opponent (capture_radius is 0, but proximity matters)
            adj_pen = 0
            if abs(nx - ox) <= 1 and abs(ny - oy) <= 1:
                adj_pen = 200
            score = -(d_far * 10 + d_op) - open_cnt * 3 - adj_pen
            if best is None or score < best_score:
                best, best_score = (dx, dy), score
        return [best[0], best[1]]