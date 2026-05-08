def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    targets = []
    for key in ("unclaimed_cells", "resources", "resource_cells"):
        pts = observation.get(key) or []
        for p in pts:
            try:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                    targets.append((x, y))
            except:
                pass
        if targets:
            break

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        if targets:
            mind = min(manh(nx, ny, tx, ty) for tx, ty in targets)
            score = -mind
        else:
            score = -manh(nx, ny, ox, oy)  # move toward opponent as fallback
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]