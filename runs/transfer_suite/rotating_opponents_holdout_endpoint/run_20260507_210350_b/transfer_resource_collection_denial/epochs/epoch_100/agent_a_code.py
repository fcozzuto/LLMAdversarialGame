def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def king_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # Avoid the opponent if possible
        best = [0, 0]
        best_d = king_dist(sx, sy, ox, oy)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = king_dist(nx, ny, ox, oy)
            if d > best_d:
                best_d = d
                best = [dx, dy]
        return best

    best_target = None
    best_score = None
    for rx, ry in resources:
        us = king_dist(sx, sy, rx, ry)
        opd = king_dist(ox, oy, rx, ry)
        # Prefer resources where we are closer; break ties by being closer overall, then by coordinates.
        score = (opd - us, -us, -(rx + 10 * ry))
        if best_score is None or score > best_score:
            best_score = score
            best_target = (rx, ry)

    rx, ry = best_target
    # If opponent is extremely threatening, step to increase distance slightly while still trending to resource.
    threat = (king_dist(sx, sy, ox, oy) <= 2)

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = king_dist(nx, ny, rx, ry)
        opp_d = king_dist(nx, ny, ox, oy)
        # Main objective: reduce distance to target; secondary: if threatened, increase separation.
        val = (-nd, opp_d if threat else 0, -(nx + 10 * ny))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move