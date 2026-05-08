def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def eval_cell(x, y):
        if not resources:
            return (-cheb(x, y, ox, oy), cheb(x, y, ox, oy), x, y)
        best = None
        for rx, ry in resources:
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources we can beat the opponent on (larger od-sd), then closer sd.
            cand = (od - sd, -sd, rx, ry)
            if best is None or cand > best:
                best = cand
        # Ensure deterministic ordering if multiple resources give same quality.
        return (best[0], best[1], best[2], best[3])

    if not resources:
        bestv = None
        bestm = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = (-cheb(nx, ny, ox, oy), nx, ny)
            if bestv is None or v > bestv:
                bestv = v
                bestm = (nx - sx, ny - sy)
        return [int(bestm[0]), int(bestm[1])]

    bestv = None
    bestm = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
        v = eval_cell(nx, ny)
        # Tie-break deterministically by cell then move.
        tie = (v, -cheb(nx, ny, ox, oy), nx, ny, dx, dy)
        if bestv is None or tie > bestv:
            bestv = tie
            bestm = (nx - sx, ny - sy)
    return [int(bestm[0]), int(bestm[1])]