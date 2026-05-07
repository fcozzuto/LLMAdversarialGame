def choose_move(observation):
    w = observation.get("grid_width")
    h = observation.get("grid_height")
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (None, None))
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            try:
                obstacles.add((int(x), int(y)))
            except:
                pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                res.append((int(p[0]), int(p[1])))
            except:
                pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(dx, dy):
        nx, ny = sx + dx, sy + dy
        return inb(nx, ny) and (nx, ny) not in obstacles

    if res:
        tx, ty = min(res, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        if ox is None or oy is None:
            tx, ty = (w - 1) // 2, (h - 1) // 2
        else:
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    best = None
    for dx, dy in moves:
        if not valid(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        score = -(abs(nx - tx) + abs(ny - ty))
        if ox is not None and oy is not None:
            score += 0.01 * (abs(nx - ox) + abs(ny - oy))
        if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))

    if best is None:
        return [0, 0]
    dx, dy = best[1]
    return [dx, dy]