def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sp[0]), int(sp[1]), int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_tr = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            self_tr.add((int(p[0]), int(p[1])))

    opp_tr = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            opp_tr.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = resources if resources else [((ox), (oy))]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = min(dist((nx, ny), t) for t in targets)
        val = -d
        if (nx, ny) in resources:
            val += 50
        if (nx, ny) in unclaimed:
            val += 10
        if (nx, ny) in self_tr:
            val += 8
        if (nx, ny) in opp_tr:
            val -= 25
        if (nx, ny) == (ox, oy):
            val += 40
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]