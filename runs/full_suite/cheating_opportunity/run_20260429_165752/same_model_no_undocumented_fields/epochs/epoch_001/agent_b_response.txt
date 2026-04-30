def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation["self_position"]
    obstacles = set(tuple(o) for o in observation.get("obstacles", []))
    resources = [tuple(r) for r in observation.get("resources", [])]

    if (x, y) in resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx if dx >= 0 else -dx if dy == 0 else (dy if dy >= 0 else -dy)  # will be overwritten

    def cheb2(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            # pick best resource deterministically from (nx, ny)
            best_res = None
            best_dist = None
            for r in resources:
                d = cheb2((nx, ny), r)
                if best_dist is None or d < best_dist or (d == best_dist and r < best_res):
                    best_dist = d
                    best_res = r
            # also softly prefer moving away from opponent if similarly good
            opp = tuple(observation.get("opponent_position", (x, y)))
            oppd = cheb2((nx, ny), opp)
            val = (best_dist, -oppd, best_res)
        else:
            val = (0, 0, (nx, ny))

        if best_val is None or val < best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best