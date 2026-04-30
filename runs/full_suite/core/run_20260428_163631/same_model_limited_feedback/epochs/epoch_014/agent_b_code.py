def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    deltas = [(0,0), (1,0), (0,1), (-1,0), (0,-1), (1,1), (-1,1), (1,-1), (-1,-1)]
    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x
    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) + abs(dy)
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    if not resources:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        obstacle_pen = -1000 if (nx, ny) in obstacles else 0
        if obstacle_pen < 0:
            score = obstacle_pen
        else:
            best_target = None
            best_target_val = -10**18
            for rx, ry in resources:
                sd = dist(nx, ny, rx, ry)
                od = dist(ox, oy, rx, ry)
                val = (od - sd) * 10 - sd
                if val > best_target_val:
                    best_target_val = val
                    best_target = (rx, ry)
            # Secondary shaping: slightly avoid getting stuck near obstacles; prefer moves that keep options
            neigh_free = 0
            for adx, ady in deltas:
                tx, ty = nx + adx, ny + ady
                if in_bounds(tx, ty) and (tx, ty) not in obstacles:
                    neigh_free += 1
            opp_to_self = dist(ox, oy, nx, ny)
            approach_opponent = -0.3 * opp_to_self
            score = obstacle_pen + best_target_val + 0.05 * neigh_free + approach_opponent
            # If we land on a resource, strongly favor it
            if (nx, ny) in set(tuple(r) for r in resources):
                score += 5000
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]