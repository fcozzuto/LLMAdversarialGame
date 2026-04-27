def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1,  0), (0,  0), (1,  0),
            (-1,  1), (0,  1), (1,  1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Strategy: move toward closest resource if any; if none, move toward goal corner
    if resources:
        best_move = (0, 0)
        best_score = None
        for rx, ry in resources:
            d_me = dist((sx, sy), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))
            # Prefer resources closer to me than opponent, and not too close to walls
            score = (d_opp - d_me) * 10 - dist((sx, sy), (rx, ry))
            if best_score is None or score > best_score:
                best_score = score
                best_move = (rx - sx, ry - sy)
        mx, my = best_move
        nx, ny = sx + (1 if mx > 0 else -1 if mx < 0 else 0), sy + (1 if my > 0 else -1 if my < 0 else 0)
        if legal(nx, ny) and (mx, my) in dirs:
            return [mx if mx != 0 else 0, my if my != 0 else 0]
        # fallback to step toward resource
        dx = 0 if mx == 0 else (1 if mx > 0 else -1)
        dy = 0 if my == 0 else (1 if my > 0 else -1)
        if legal(sx + dx, sy + dy):
            return [dx, dy]
        # else try any legal neighbor toward resource
        for dx2, dy2 in [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]:
            nx, ny = sx + dx2, sy + dy2
            if legal(nx, ny):
                return [dx2, dy2]
        return [0,0]
    else:
        # No resources: head toward opponent to contest space but avoid obstacles
        dx = 0
        dy = 0
        if ox > sx: dx = 1
        elif ox < sx: dx = -1
        if oy > sy: dy = 1
        elif oy < sy: dy = -1
        if legal(sx + dx, sy + dy):
            return [dx, dy]
        # try alternatives
        for ax, ay in dirs:
            nx, ny = sx + ax, sy + ay
            if legal(nx, ny):
                return [ax, ay]
        return [0,0]