def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = observation.get("obstacles") or []
    blocked = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    resources = observation.get("resources") or []
    best = None
    target_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            target_list.append((int(r[0]), int(r[1])))

    if target_list:
        for tx, ty in target_list:
            key = (manh(sx, sy, tx, ty), tx, ty)
            if best is None or key < best[0]:
                best = (key, tx, ty)
        tx, ty = best[1], best[2]
        best_move = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Prefer reducing our distance; small deterministic tie-breakers to avoid jitter.
            score = (manh(nx, ny, tx, ty), manh(nx, ny, ox, oy), nx, ny)
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move if best_move is not None else [0, 0]

    tx, ty = w // 2, h // 2
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = (manh(nx, ny, tx, ty), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move if best_move is not None else [0, 0]