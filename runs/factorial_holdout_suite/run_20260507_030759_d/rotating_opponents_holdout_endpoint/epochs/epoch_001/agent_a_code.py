def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    moves.append((0, 0))
    if resources:
        best = None
        for rx, ry in resources:
            d = dist(sx, sy, rx, ry)
            key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
        step_dx = 0 if tx == sx else (1 if tx > sx else -1)
        step_dy = 0 if ty == sy else (1 if ty > sy else -1)
        cand = (step_dx, step_dy)
        cx, cy = sx + cand[0], sy + cand[1]
        if inb(cx, cy) and (cx, cy) not in obstacles:
            return [cand[0], cand[1]]
        ordered = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            ordered.append(((dist(nx, ny, tx, ty), dx, dy), (dx, dy)))
        if ordered:
            ordered.sort(key=lambda t: t[0])
            return [ordered[0][1][0], ordered[0][1][1]]
        return [0, 0]
    else:
        # No resources visible: move toward opponent deterministically
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                d = dist(nx, ny, ox, oy)
                key = (d, dx, dy)
                if best is None or key < best[0]:
                    best = (key, (dx, dy))
        return [best[1][0], best[1][1]] if best else [0, 0]