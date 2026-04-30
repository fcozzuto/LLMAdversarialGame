def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    if not resources:
        dx = 0 if sx == ox else (1 if sx < ox else -1)
        dy = 0 if sy == oy else (1 if sy < oy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    for rx, ry in resources:
        d_self = dist(sx, sy, rx, ry)
        d_opp = dist(ox, oy, rx, ry)
        # Prefer resources we can reach sooner (or that opponent is far from).
        key = (d_self - d_opp, d_self, (rx, ry))
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # Greedy step toward target; if blocked, choose best feasible alternative.
    def feasible(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    options = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if feasible(nx, ny):
            options.append((dist(nx, ny, tx, ty), dist(nx, ny, ox, oy), (dx, dy)))
    options.sort(key=lambda t: (t[0], t[1], t[2]))
    if options:
        return [options[0][2][0], options[0][2][1]]
    return [0, 0]