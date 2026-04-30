def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = [(dx, dy) for dx, dy in deltas if inside(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    if resources:
        resources_sorted = sorted(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))
        cand = resources_sorted[:3]
        best = (0, 0)
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            score = 10**9
            for rx, ry in cand:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                score = score if od - sd < score else od - sd  # min advantage across candidates
            if score > best_score:
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]]

    # No resources visible: try to move toward opponent's side to increase pressure deterministically
    best = (0, 0)
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Prefer decreasing distance to opponent while not getting stuck
        score = -(cheb(nx, ny, ox, oy))
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]