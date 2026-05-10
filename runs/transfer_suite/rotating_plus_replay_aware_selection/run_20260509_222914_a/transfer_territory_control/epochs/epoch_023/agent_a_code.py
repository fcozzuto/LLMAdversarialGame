def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2 and isinstance(p[0], int) and isinstance(p[1], int):
            if inside(p[0], p[1]): obstacles.add((p[0], p[1]))

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    unclaimed = observation.get("unclaimed_cells") or []
    resources = observation.get("resources") or []

    def manhattan(x, y, a, b): return abs(x - a) + abs(y - b)

    def score_cell(x, y):
        s = 0
        if (x, y) in obstacles: return -10**9
        s -= manhattan(x, y, ox, oy) * 3
        if (x, y) in unclaimed: s += 10
        if resources:
            bestr = min((manhattan(x, y, int(r[0]), int(r[1])) for r in resources
                         if isinstance(r, (list, tuple)) and len(r) >= 2
                         and isinstance(r[0], int) and isinstance(r[1], int)), default=10**9)
            s += max(0, 8 - bestr)
        return s

    best = None
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        s = score_cell(nx, ny)
        if s > best_s:
            best_s, best = s, [dx, dy]
    if best is not None:
        return best

    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]