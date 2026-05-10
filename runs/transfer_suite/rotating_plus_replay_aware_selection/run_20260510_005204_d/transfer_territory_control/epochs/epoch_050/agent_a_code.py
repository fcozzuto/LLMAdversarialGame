def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def best_point(key):
        pts = []
        for p in (observation.get(key) or []):
            if p and len(p) >= 2:
                pts.append((int(p[0]), int(p[1])))
        if not pts:
            return None
        best = pts[0]
        bd = abs(best[0] - sx) + abs(best[1] - sy)
        for q in pts[1:]:
            d = abs(q[0] - sx) + abs(q[1] - sy)
            if d < bd:
                bd = d
                best = q
        return best

    target = best_point("resources")
    if target is None:
        target = best_point("unclaimed_cells")
    if target is None:
        target = (max(0, min(w - 1, w // 2)), max(0, min(h - 1, h // 2)))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    best_move = moves[0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        d = abs(nx - target[0]) + abs(ny - target[1])
        score = -d
        if (nx, ny) in unclaimed:
            score += 20
        if abs(nx - ox) + abs(ny - oy) <= 1:
            score -= 2
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    if (sx + best_move[0], sy + best_move[1]) in obstacles or sx + best_move[0] < 0 or sx + best_move[0] >= w or sy + best_move[1] < 0 or sy + best_move[1] >= h:
        return [0, 0]
    return best_move