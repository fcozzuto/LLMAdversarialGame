def choose_move(observation):
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    targets = []
    res = observation.get("resources", None)
    if res is not None:
        for p in res or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                targets.append((int(p[0]), int(p[1])))
    if not targets:
        uc = observation.get("unclaimed_cells", []) or []
        for p in uc:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                targets.append((int(p[0]), int(p[1])))

    if not targets:
        targets = [(int(ox), int(oy))]

    def clamp_in(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = int(x + dx), int(y + dy)
        if not clamp_in(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        td = min(dist(nx, ny, tx, ty) for tx, ty in targets)
        score = td
        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]
    if best is not None:
        return best

    for dx, dy in moves:
        nx, ny = int(x + dx), int(y + dy)
        if clamp_in(nx, ny):
            return [dx, dy]
    return [0, 0]