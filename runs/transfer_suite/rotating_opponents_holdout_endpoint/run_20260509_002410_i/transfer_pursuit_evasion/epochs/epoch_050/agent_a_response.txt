def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in self_role) or (self_role == "evader")
    is_pursuer = ("pursuer" in self_role) or (self_role == "pursuer")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def dist(x, y, x2, y2):
        return (x - x2) * (x - x2) + (y - y2) * (y - y2)

    def obs_pen(x, y):
        if (x, y) in obstacles:
            return 10**9
        pen = 0
        for (ox2, oy2) in obstacles:
            md = abs(x - ox2) + abs(y - oy2)
            if md == 0:
                return 10**9
            if md == 1: pen += 5
            elif md == 2: pen += 2
        return pen

    def corner_bias(x, y):
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        # deterministic: tie-break by fixed corner order
        best = -10**18
        for (cx, cy) in corners:
            val = abs(cx - ox) + abs(cy - oy)
            if val > best:
                best = val
                bc = (cx, cy)
        # if evader, go to corner far from opponent; if pursuer, go to corner near opponent
        return (abs(x - bc[0]) + abs(y - bc[1]))

    best_move = (0, 0)
    best_score = -10**18 if is_evader or not is_pursuer else 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if is_evader or not is_pursuer:
            # maximize squared distance; avoid obstacles; also avoid staying too central if corner runner helps
            score = dist(nx, ny, ox, oy) - 2.0 * obs_pen(nx, ny) - 0.03 * corner_bias(nx, ny)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            # pursuer: minimize squared distance to opponent; avoid obstacles; prefer corridor toward opponent
            score = dist(nx, ny, ox, oy) + 2.0 * obs_pen(nx, ny) + 0.03 * corner_bias(nx, ny)
            if score < best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]