def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = observation["resources"]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]

    if resources:
        target = min(resources, key=lambda r: (dist((sx, sy), (r[0], r[1])), r[0], r[1]))
    else:
        target = (ox, oy)

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist((nx, ny), target)
        key = (d, nx, ny)
        if best is None or key < best[0]:
            best = (key, (dx, dy))

    if best is not None:
        return [best[1][0], best[1][1]]

    return [0, 0]