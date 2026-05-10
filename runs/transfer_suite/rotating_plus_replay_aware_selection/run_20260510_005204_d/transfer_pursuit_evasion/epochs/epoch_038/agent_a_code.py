def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()

    if "evader" in self_role:
        is_evader = True
    elif "pursuer" in self_role:
        is_evader = False
    else:
        is_evader = ("evader" in opponent_role) and ("pursuer" in self_role) == False

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    obstacles = list(blocked)

    def dist_cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    def min_obs_manh(x, y):
        if not obstacles:
            return 999
        best = 999
        for (bx, by) in obstacles:
            d = abs(x - bx) + abs(y - by)
            if d < best:
                best = d
        return best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist_cheb(nx, ny)
        m = min_obs_manh(nx, ny)
        if is_evader:
            cand.append((-d, -m, dx, dy))  # maximize d and m
        else:
            cand.append((d, -m, dx, dy))   # minimize d, then maximize m
    if not cand:
        return [0, 0]

    cand.sort()
    _, _, dx, dy = cand[0]
    return [int(dx), int(dy)]