def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    W = observation.get("grid_width", 0)
    H = observation.get("grid_height", 0)

    resources = observation.get("resources")
    if not resources:
        resources = []
    obstacles = observation.get("obstacles")
    if not obstacles:
        obstacles = []

    obs_set = set()
    for o in obstacles:
        try:
            x, y = o
            obs_set.add((int(x), int(y)))
        except:
            pass

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target = None
    best_key = None
    for rx, ry in resources:
        rs = man(sx, sy, rx, ry)
        ro = man(ox, oy, rx, ry)
        key = (rs - ro, rs, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            target = (rx, ry)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if target is None:
        return [0, 0]

    rx, ry = target
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue
        d_self = man(nx, ny, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        score = (d_self - d_opp, d_self, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move