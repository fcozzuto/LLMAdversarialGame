def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obs_list = observation.get("obstacles", [])
    obstacles = set(tuple(p) for p in obs_list)

    resources = observation.get("resources", []) or []
    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    target = None
    best = -10**9
    for p in resources:
        if tuple(p) in obstacles:
            continue
        val = dist((ox, oy), p) - dist((sx, sy), p)
        if val > best or (val == best and dist((sx, sy), p) < dist((sx, sy), target) if target else True):
            best = val
            target = tuple(p)

    aim = (ox, oy)
    if target is not None:
        if dist((ox, oy), target) + 2 <= dist((sx, sy), target):
            aim = (ox, oy)
        else:
            aim = target

    best_move = (0, 0)
    best_score = -10**18
    cur_d = dist((sx, sy), aim)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), aim)
        score = (cur_d - nd) * 100 - nd
        if dx == 0 and dy == 0:
            score -= 1
        if (nx, ny) in resources:
            score += 30
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move