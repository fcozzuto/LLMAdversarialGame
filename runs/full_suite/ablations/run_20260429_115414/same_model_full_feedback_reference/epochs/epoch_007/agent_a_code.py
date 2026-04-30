def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except:
            pass

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y):
        return 0 <= x < W and 0 <= y < H
    def legal(x, y):
        return inb(x, y) and (x, y) not in obs
    def dist(a, b, c, d):
        dx = a - c; dx = -dx if dx < 0 else dx
        dy = b - d; dy = -dy if dy < 0 else dy
        return dx + dy

    legal_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            legal_moves.append((dx, dy))

    if not legal_moves:
        return [0, 0]

    if resources:
        best = None
        for dx, dy in legal_moves:
            nx, ny = sx + dx, sy + dy
            my = None
            op = None
            for r in resources:
                rx, ry = r[0], r[1]
                d1 = dist(nx, ny, rx, ry)
                if my is None or d1 < my: my = d1
                d2 = dist(ox, oy, rx, ry)
                if op is None or d2 < op: op = d2
            # higher is better: get closer to resources than opponent
            score = (op - my) * 1000 - (abs(nx - ox) + abs(ny - oy))
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]
    else:
        # no resources: move toward opponent to pressure
        tx = 0
        ty = 0
        if ox > sx: tx = 1
        elif ox < sx: tx = -1
        if oy > sy: ty = 1
        elif oy < sy: ty = -1
        # choose the legal move that matches the step direction best
        best = None
        for dx, dy in legal_moves:
            score = -(abs(dx - tx) + abs(dy - ty))
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]