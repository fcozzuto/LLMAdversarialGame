def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            resources.append((int(p[0]), int(p[1]), p[2] if len(p) > 2 else 1))
    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(x, y):
        if not inb(x, y) or (x, y) in obstacles:
            return -10**9
        d_opp = abs(x - ox) + abs(y - oy)
        want = 0
        if resources:
            d_res = min(abs(x - rx) + abs(y - ry) for (rx, ry, _) in resources)
            want += 20 / (1 + d_res)
        if unclaimed:
            want += 2.5 if (x, y) in unclaimed else 0
        want += 0.8 * d_opp
        if (x, y) == (ox, oy):
            want -= 15
        return want

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = score_cell(nx, ny)
        if v > bestv:
            bestv = v
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]