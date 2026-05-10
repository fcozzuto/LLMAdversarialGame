def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not w or not h:
        return [0, 0]
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    resources = set(map(tuple, observation.get("resources", [])))
    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: man(sx, sy, p[0], p[1]))
    elif resources:
        tx, ty = min(resources, key=lambda p: man(sx, sy, p[0], p[1]))
    else:
        tx, ty = ox, oy

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist_t = man(nx, ny, tx, ty)
        dist_o = man(nx, ny, ox, oy)
        s = -dist_t
        if (nx, ny) in unclaimed:
            s += 3
        if dist_o == 0:
            s -= 5
        elif dist_o <= 2:
            s -= 1
        if s > best_score:
            best_score = s
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best