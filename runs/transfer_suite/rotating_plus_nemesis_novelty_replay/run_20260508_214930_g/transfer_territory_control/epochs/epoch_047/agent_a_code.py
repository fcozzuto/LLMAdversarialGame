def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = list(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    resources = list(tuple(p) for p in (observation.get("resources") or []))

    dirs = [(-1, 0), (0, 1), (1, 0), (0, -1), (0, 0), (-1, -1), (1, -1), (1, 1), (-1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = unclaimed if unclaimed else resources
    best = None
    bestv = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if targets:
            d_self = min(dist((nx, ny), t) for t in targets)
            # prefer closer to targets, but also keep away from opponent
            d_opp = dist((nx, ny), (ox, oy))
            v = 50 * (-d_self) + 3 * d_opp
        else:
            # no targets: move away from opponent (tie-break by deterministic direction order)
            v = dist((nx, ny), (ox, oy))
        if v > bestv:
            bestv = v
            best = [dx, dy]

    if best is not None:
        return best

    # If all moves blocked, return a deterministic safe move if possible, else 0,0.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            return [dx, dy]
    return [0, 0]