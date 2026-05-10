def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    resources = observation.get("resources") or []
    best_resource = None
    best_rd = 10**9
    for p in resources:
        x, y = p[0], p[1]
        if not inb(x, y) or (x, y) in obstacles:
            continue
        d = dist(sx, sy, x, y)
        if d < best_rd:
            best_rd = d
            best_resource = (x, y)

    target = best_resource if (best_resource is not None and (observation.get("remaining_resource_count", 1) or 0) > 0) else (ox, oy)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_target = dist(nx, ny, target[0], target[1])
        d_to_opp = dist(nx, ny, ox, oy)
        score = -d_to_target + 0.2 * d_to_opp
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [int(dx), int(dy)]