def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    rem = observation.get("remaining_resource_count", 0)
    try:
        rem = int(rem or 0)
    except:
        rem = 0
    late = rem <= 2

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            d_self = min(dist(nx, ny, rx, ry) for rx, ry in resources)
            d_opp = min(dist(ox, oy, rx, ry) for rx, ry in resources)
            score = (10 if d_self == 0 else 0) + (2 if d_self <= 1 else 0)
            score += (d_opp - d_self) if late else (d_opp * 0.1 - d_self)
        else:
            score = dist(nx, ny, w - 1, h - 1)  # deterministic drift
            if late:
                score = -dist(nx, ny, ox, oy)  # move away when resources exhausted
        if best_score is None or score > best_score or (score == best_score and (best is None or (dx, dy) < best)):
            best_score = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]