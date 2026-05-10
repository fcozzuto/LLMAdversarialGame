def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cell_value(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in self_terr:
            return 1
        if (x, y) in opp_terr:
            return 8
        if (x, y) in unclaimed:
            return 5
        return 0

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dv = manh(nx, ny, ox, oy)
        score = cell_value(nx, ny) * 100 - dv
        if (nx, ny) in self_terr:
            score += 20
        if (nx, ny) in opp_terr:
            score += 30
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best