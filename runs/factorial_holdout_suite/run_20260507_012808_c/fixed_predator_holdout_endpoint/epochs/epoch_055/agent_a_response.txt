def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
    if not resources:
        return [0, 0]

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_score = None
    best_move = (0, 0)

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        self_min = 10**9
        opp_min = 10**9
        for rx, ry in resources:
            sd = king_dist(nx, ny, rx, ry)
            if sd < self_min: self_min = sd
            od = king_dist(ox, oy, rx, ry)
            if od < opp_min: opp_min = od

        # Prefer states where we're closer than opponent to nearest resource; tie-break for being even closer.
        score = (opp_min - self_min, -self_min, dxm, dym)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]