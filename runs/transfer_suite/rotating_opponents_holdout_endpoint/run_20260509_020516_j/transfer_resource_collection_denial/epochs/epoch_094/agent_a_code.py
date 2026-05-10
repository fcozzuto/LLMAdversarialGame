def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    def parse_pos(p, default_x, default_y):
        try:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                return int(x), int(y)
        except:
            pass
        return int(default_x), int(default_y)

    sx, sy = parse_pos(observation.get("self_position"), 0, 0)
    ox, oy = parse_pos(observation.get("opponent_position"), w - 1, h - 1)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                x, y = int(r[0]), int(r[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    resources.append((x, y))
        except:
            pass

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = (0, 0)
    best_score = None

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            nearest = min(md(nx, ny, rx, ry) for rx, ry in resources)
            score = nearest
            if best_score is None or score < best_score or (score == best_score and (dx, dy) < best):
                best_score, best = score, (dx, dy)
    else:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            score = md(nx, ny, ox, oy)
            if best_score is None or score < best_score or (score == best_score and (dx, dy) < best):
                best_score, best = score, (dx, dy)

    return [int(best[0]), int(best[1])]