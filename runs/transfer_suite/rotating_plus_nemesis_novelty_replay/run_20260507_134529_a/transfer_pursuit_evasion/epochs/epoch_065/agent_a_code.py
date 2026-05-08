def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = 0
        if resources:
            dmin = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            score += 1000 - 50 * dmin
        if is_evader:
            dopp = cheb(nx, ny, ox, oy)
            score += 50 * dopp
        else:
            dopp = cheb(nx, ny, ox, oy)
            score += 50 * (-dopp)
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if ok(sx, sy):
        return best
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            return [dx, dy]
    return [0, 0]