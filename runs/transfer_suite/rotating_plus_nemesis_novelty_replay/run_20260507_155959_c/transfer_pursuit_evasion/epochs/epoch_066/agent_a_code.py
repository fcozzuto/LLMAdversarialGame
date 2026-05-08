def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    role = (observation.get("self_role", "") or "").lower()
    evader = ("evad" in role) or ("runner" in role) or ("evasion" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    res = observation.get("resources", None)
    resources = []
    if isinstance(res, (list, tuple)):
        for p in res:
            try:
                x, y = p
                resources.append((int(x), int(y)))
            except Exception:
                pass
    if not resources:
        resources = None

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            d = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            val = -d
        else:
            dfo = cheb(nx, ny, ox, oy)
            val = dfo if evader else -dfo
        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]