def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def best_target_value(px, py):
        if not resources:
            return -10**9, None, 0, 0
        bestv = -10**9
        bestr = None
        bs = bo = 0
        for r in resources:
            sd = dist((px, py), r)
            od = dist((ox, oy), r)
            v = (od - sd) * 8 - sd * 2
            # Slight preference to avoid moving into immediate contest disadvantage
            if od <= sd:
                v -= 6
            if v > bestv:
                bestv, bestr, bs, bo = v, r, sd, od
        return bestv, bestr, bs, bo

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        v, r, sd, od = best_target_value(nx, ny)
        # Defensive term: if no good target, steer toward resources but reduce distance to opponent
        # (prevents getting stuck while opponent takes all resources)
        if r is None:
            score = -sd * 3 - dist((nx, ny), (ox, oy)) * 1
        else:
            score = v * 10 - dist((nx, ny), (ox, oy)) * 2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]