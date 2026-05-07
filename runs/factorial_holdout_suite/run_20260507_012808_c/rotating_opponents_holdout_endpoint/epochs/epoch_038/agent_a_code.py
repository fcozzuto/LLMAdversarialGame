def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (0, 0)))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            deltas.append((dx, dy))

    def nearest_res_dist(px, py):
        best = None
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if best is None or d < best:
                best = d
        return best

    best_move = (0, 0)
    best_score = None
    # New policy: simultaneously approach resources and avoid being the easiest target
    # for opponent; prefer moves that increase distance to opponent when resource access is similar.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_res = nearest_res_dist(nx, ny)
        d_opp = cheb(nx, ny, ox, oy)
        # Strong priority to collection, then keep away from opponent
        score = (-1000 * d_res) + (50 * d_opp) - (1 if (nx, ny) in resources else 0)
        # Deterministic tie-breaker: prefer staying, then lexicographic dx,dy
        if best_score is None or score > best_score or (score == best_score and ((dx, dy) < best_move)):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]