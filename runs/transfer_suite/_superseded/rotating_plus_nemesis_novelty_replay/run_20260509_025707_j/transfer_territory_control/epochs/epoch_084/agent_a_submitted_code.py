def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w, h = observation.get("grid_width", 0), observation.get("grid_height", 0)
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]
    obstacles = set(observation.get("obstacles") or [])
    opp_pos = observation.get("opponent_position", (sx, sy))
    opp_terr = set(observation.get("opponent_territory") or [])
    un = set(observation.get("unclaimed_cells") or [])
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            if (nx, ny) in opp_terr:
                return [dx, dy]
            candidates.append((dx, dy))

    if not candidates:
        return [0, 0]

    if un:
        target = min(un, key=lambda p: dist(p, opp_pos))
        best = min(candidates, key=lambda m: dist((sx + m[0], sy + m[1]), target))
        return [best[0], best[1]]

    best = min(candidates, key=lambda m: dist((sx + m[0], sy + m[1]), opp_pos))
    return [best[0], best[1]]