def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if resources:
        best_r = None
        best_m = None
        for rx, ry in resources:
            m = abs(rx - sx) + abs(ry - sy)
            if best_m is None or m < best_m or (m == best_m and (rx, ry) < best_r):
                best_m = m
                best_r = (rx, ry)
        tx, ty = best_r
        best_move = None
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dt = abs(tx - nx) + abs(ty - ny)
            do = abs(ox - nx) + abs(oy - ny)
            score = (-2 * dt) + (0.5 * do)
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]] if best_move is not None else [0, 0]
    else:
        tx, ty = ox, oy
        best_move = None
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dt = abs(tx - nx) + abs(ty - ny)
            score = -dt
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]] if best_move is not None else [0, 0]