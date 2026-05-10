def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = []
    for p in resources:
        if p and len(p) >= 2:
            res.append((p[0], p[1]))
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If no resources, drift toward opponent (deterministic fallback).
    if not res:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
        for ddx, ddy in [(dx, 0), (0, dy), (dx, ddy), (0, 0)]:
            nx, ny = sx + ddx, sy + ddy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [ddx, ddy]
        return [0, 0]

    best_move = [0, 0]
    best_val = -10**18

    # Deterministic tie-breaking: choose lexicographically smallest move among equals.
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        move_val = 0
        if (nx, ny) in set(res):
            move_val += 10**6

        # Choose resource that best suits us while denying it to opponent.
        local_best = -10**18
        for rx, ry in res:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)

            # Primary: get closer; Secondary: be earlier than opponent; Tertiary: reduce opponent access.
            val = (-my_d * 1000) + (op_d - my_d) * 50 + (1 / (1 + my_d)) * 10
            if val > local_best:
                local_best = val

        move_val += local_best

        if move_val > best_val:
            best_val = move_val
            best_move = [ddx, ddy]
        elif move_val == best_val:
            if [ddx, ddy] < best_move:
                best_move = [ddx, ddy]

    if best_move != [0, 0]:
        return best_move

    # If all candidate moves blocked, try staying.
    if (sx, sy) not in obs:
        return [0, 0]

    # Otherwise pick any legal neighbor.
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [ddx, ddy]
    return [0, 0]