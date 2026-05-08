def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    best = None
    best_score = None

    if not resources:
        # Fallback: drift away from opponent slightly, avoid obstacles
        cand = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy))
        if not cand:
            return [0, 0]
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            score = dist(nx, ny, ox, oy)
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Prefer moves that reduce distance to nearest resource.
        my_d = min(dist(nx, ny, rx, ry) for rx, ry in resources)

        # If opponent is closer to that region, penalize.
        op_d = min(dist(ox, oy, rx, ry) for rx, ry in resources)

        # Strongly prefer capturing/approaching when we are closer; also add tie-break toward center-ish.
        score = (op_d - my_d) * 1000 - my_d
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]