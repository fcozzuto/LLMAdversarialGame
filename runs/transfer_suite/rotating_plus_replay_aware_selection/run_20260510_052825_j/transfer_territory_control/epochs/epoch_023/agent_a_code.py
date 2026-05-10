def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    resources = list(observation.get("resources") or [])

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def inside(a, b):
        return 0 <= a < w and 0 <= b < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def nearest_resource_dist(nx, ny):
        if not resources:
            return 0
        best = None
        for r in resources:
            try:
                rx, ry = r
            except Exception:
                continue
            if inside(rx, ry):
                d = man(nx, ny, rx, ry)
                if best is None or d < best:
                    best = d
        return best if best is not None else 0

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        adj_unclaimed = 0
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ax, ay = nx + ddx, ny + ddy
            if inside(ax, ay) and (ax, ay) in unclaimed:
                adj_unclaimed += 1
        d_opp = man(nx, ny, ox, oy)
        nr = nearest_resource_dist(nx, ny)
        val = adj_unclaimed * 10 + d_opp - (nr if nr else 0)
        if (adj_unclaimed > 0 and (nx, ny) in unclaimed) or (d_opp > man(x, y, ox, oy)):
            val += 1
        if val > best_val or (val == best_val and (dx, dy) == (0, 0)):
            best_val = val
            best_move = [dx, dy]

    return best_move