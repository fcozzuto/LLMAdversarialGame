def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    try:
        w, h = int(w), int(h)
    except:
        w, h = 8, 8

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, w - 1, h - 1

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                try:
                    x, y = int(x), int(y)
                except:
                    continue
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**30

    def dsq(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        score = 0
        if unclaimed:
            if (nx, ny) in unclaimed:
                score += 10**6
            else:
                score -= 10**3
            # mild bias: prefer being farther from opponent while staying near unclaimed
            nearest = None
            for ux, uy in unclaimed:
                d = dsq(nx, ny, ux, uy)
                if nearest is None or d < nearest:
                    nearest = d
            if nearest is not None:
                score += max(0, 200 - nearest)
        score += dsq(nx, ny, ox, oy)  # avoid getting close
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]