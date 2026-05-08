def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    resources = observation.get("resources", []) or []
    want_resource = bool(resources) or (observation.get("remaining_resource_count", 0) or 0) > 0

    tx, ty = ox, oy
    if want_resource:
        best = None
        for r in resources:
            try:
                x, y = r if isinstance(r, (list, tuple)) and len(r) >= 2 else (None, None)
            except Exception:
                continue
            if x is None or y is None:
                continue
            x, y = int(x), int(y)
            if inb(x, y) and (x, y) not in obs:
                d = abs(x - sx) + abs(y - sy)
                if best is None or d < best:
                    best = d
                    tx, ty = x, y

    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = abs(nx - ox) + abs(ny - oy)
        if want_resource and resources:
            score = (abs(nx - tx) + abs(ny - ty), score)
        if best_move is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move is None:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return best_move