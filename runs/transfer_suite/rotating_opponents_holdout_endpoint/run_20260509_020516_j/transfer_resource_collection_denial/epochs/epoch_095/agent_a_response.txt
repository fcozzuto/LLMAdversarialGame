def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    def pos(p, dx=0, dy=0):
        try:
            return int(p[0]), int(p[1])
        except:
            return dx, dy

    sx, sy = pos(observation.get("self_position"), 0, 0)
    ox, oy = pos(observation.get("opponent_position"), w - 1, h - 1)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for p in observation.get("resources") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_target(ex, ey):
        best = None
        for rx, ry in resources:
            sd = md(ex, ey, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd
            # prefer winning/close targets deterministically
            cand = (adv, -sd, -rx, -ry)
            if best is None or cand > best[0]:
                best = (cand, rx, ry, sd, od)
        return best[1], best[2], best[3], best[4]

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        tx, ty, sd, od = best_target(nx, ny)
        # primary: out-race opponent to some resource; secondary: reduce own distance
        # tertiary: prefer positions that move generally toward the best target
        toward = (1 if nx != tx else 0) + (1 if ny != ty else 0)
        val = (od - sd, -sd, toward, -abs(nx - sx) - abs(ny - sy), nx - sx, ny - sy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]