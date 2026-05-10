def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    res = observation.get("resources", []) or []
    resources = []
    for p in res:
        if p is not None and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx*dx + dy*dy

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            nd = min(d2(nx, ny, rx, ry) for rx, ry in resources)
            score = (nd, d2(nx, ny, ox, oy), nx, ny)
        else:
            score = (d2(nx, ny, ox, oy), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]