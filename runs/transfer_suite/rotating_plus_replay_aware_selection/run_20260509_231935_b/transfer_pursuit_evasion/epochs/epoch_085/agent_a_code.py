def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    evader = ("evad" in self_role) or ("run" in self_role) or ("escape" in self_role) or ("hare" in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # deterministic tie-break: prefer not staying, then prefer reducing/increasing both axes
    order = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    move_list = [m for m in order if m in moves] + [m for m in moves if m not in order]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    best_key = None
    for dx, dy in move_list:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        if evader:
            # maximize distance; if tie, move away on both axes; avoid corners traps by preferring center-ish
            score = dist
            awayx = (dx != 0 and ((ox - nx) * (ox - sx) < 0)) or (dx == 0)
            awayy = (dy != 0 and ((oy - ny) * (oy - sy) < 0)) or (dy == 0)
            center = abs((nx - (w - 1) / 2.0)) + abs((ny - (h - 1) / 2.0))
            key = (-score, -(1 if awayx else 0) - (1 if awayy else 0), center, 0 if (dx == 0 and dy == 0) else -1)
        else:
            # minimize distance; if tie, reduce both axis distances when possible
            score = dist
            dirx = 0
            if ox != sx:
                dirx = 1 if (dx == (1 if ox > sx else -1)) else 0
            diry = 0
            if oy != sy:
                diry = 1 if (dy == (1 if oy > sy else -1)) else 0
            reduce_both = -(dirx + diry)
            key = (score, reduce_both, 0 if (dx == 0 and dy == 0) else -1)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]