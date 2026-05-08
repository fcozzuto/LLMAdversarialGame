def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                oset.add((x, y))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in oset

    role = (observation.get("self_role", "") or "").lower()
    evader = ("evad" in role) and ("purs" not in role)

    res = observation.get("resources", []) or []
    nearest = None
    bestd = 10**9
    for p in res:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in oset:
                d = abs(x - sx) + abs(y - sy)
                if d < bestd:
                    bestd, nearest = d, (x, y)

    tx, ty = nearest if (nearest is not None and not evader) else (ox, oy)

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best_move = None
    if evader:
        best_val = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            val = abs(nx - ox) + abs(ny - oy)
            if val > best_val:
                best_val, best_move = val, [dx, dy]
    else:
        best_val = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            val = abs(nx - tx) + abs(ny - ty)
            if val < best_val:
                best_val, best_move = val, [dx, dy]
    if best_move is None:
        for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best_move