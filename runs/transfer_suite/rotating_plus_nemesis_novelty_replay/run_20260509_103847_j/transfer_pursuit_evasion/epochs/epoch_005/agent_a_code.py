def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    is_evader = "evad" in role

    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        od = d2(nx, ny, ox, oy)
        if res:
            if is_evader:
                rd = max(d2(nx, ny, rx, ry) for rx, ry in res)
                score = rd + 0.3 * od
            else:
                rd = min(d2(nx, ny, rx, ry) for rx, ry in res)
                score = -rd + 0.2 * od
        else:
            score = (od if is_evader else -od)
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score
    return [best[0], best[1]]