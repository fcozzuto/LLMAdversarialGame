def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return (x, y) not in obstacles

    def bfs_dist(start, goal, maxd=6):
        if start == goal:
            return 0
        frontier = [start]
        seen = {start: 0}
        for d in range(1, maxd + 1):
            new_frontier = []
            for x, y in frontier:
                for dx, dy in moves:
                    nx, ny = x + dx, y + dy
                    if not inb(nx, ny) or not ok(nx, ny):
                        continue
                    if (nx, ny) in seen:
                        continue
                    seen[(nx, ny)] = d
                    if (nx, ny) == goal:
                        return d
                    new_frontier.append((nx, ny))
            if not new_frontier:
                break
            frontier = new_frontier
        return 10**6

    targets = []
    for r in resources:
        rx, ry = r[0], r[1]
        ds = bfs_dist((sx, sy), (rx, ry), 6)
        do = bfs_dist((ox, oy), (rx, ry), 6)
        # Prefer winning race; break ties deterministically by resource position.
        targets.append((do - ds, -ds, -do, rx, ry))
    targets.sort(reverse=True)
    _, _, _, tx, ty = targets[0]

    # Choose the move that most reduces our estimated distance to the chosen target.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or not ok(nx, ny):
            continue
        nd = bfs_dist((nx, ny), (tx, ty), 6)
        key = (-nd, abs((nx - tx)) + abs((ny - ty)), dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]