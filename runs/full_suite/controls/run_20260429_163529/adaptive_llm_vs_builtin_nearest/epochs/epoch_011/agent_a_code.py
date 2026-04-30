def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            try:
                obs.add((int(p[0]), int(p[1])))
            except:
                pass

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = observation.get("resources") or []
    closest = None
    bestd = None
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if in_bounds(rx, ry):
                d = cheb(sx, sy, rx, ry)
                if bestd is None or d < bestd:
                    bestd, closest = d, (rx, ry)
    if closest is None:
        closest = (ox, oy)

    deltas = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    tx, ty = closest
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d_target = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Prefer moving onto resources (if they exist), avoid getting too close to opponent.
        score = -d_target
        if (nx, ny) in resources:
            score += 1000
        score += (d_opp * 0.5)
        if (nx, ny) == (ox, oy):
            score -= 2000
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move if best_move else [0, 0]