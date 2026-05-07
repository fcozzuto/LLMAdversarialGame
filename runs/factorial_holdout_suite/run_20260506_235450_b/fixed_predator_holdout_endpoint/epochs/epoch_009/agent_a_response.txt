def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    tr = observation.get("turns_remaining", 0)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)
    if not resources:
        return [0, 0]
    late = (tr <= 6)
    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        if late:
            key = (-sd, -od, rx, ry)  # greedily finish
        else:
            gap = od - sd  # positive means we are closer
            # Prefer resources we can plausibly win soon; also avoid those too close to opponent
            risk = min(od, sd)
            key = (gap, -od, -(sd + 2 * risk), rx, ry)
        if best_key is None or key > best_key:
            best_key, best_r = key, (rx, ry)
    rx, ry = best_r
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = dist(nx, ny, rx, ry)
        d_opp = dist(nx, ny, ox, oy)
        d_opp_towards = dist(ox, oy, rx, ry) - dist(nx, ny, rx, ry)
        # Encourage getting closer to target and (when possible) staying farther from opponent
        score = (-d_self, d_opp, d_opp_towards, -abs(nx - rx) - abs(ny - ry), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move