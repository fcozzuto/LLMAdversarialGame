def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def mdist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    target_list = unclaimed if unclaimed else (resources if resources else [(ox, oy)])
    best_t = min(target_list, key=lambda t: mdist((sx, sy), t))

    best = (10**9, 0, 0)
    for dx, dy in moves:
        if dx == 0 and dy == 0:
            continue
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = mdist((nx, ny), best_t)
        if d < best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
            best = (d, dx, dy)

    if best[1] != 0 or best[2] != 0:
        return [best[1], best[2]]
    return [0, 0]