def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    self_set = set()
    for p in observation.get("self_territory", []) or []:
        try:
            self_set.add((int(p[0]), int(p[1])))
        except:
            pass

    opp_set = set()
    for p in observation.get("opponent_territory", []) or []:
        try:
            opp_set.add((int(p[0]), int(p[1])))
        except:
            pass

    unclaimed = set()
    for p in observation.get("unclaimed_cells", []) or []:
        try:
            unclaimed.add((int(p[0]), int(p[1])))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    nbs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = (0, 0)
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = 0.0
        if (nx, ny) in opp_set:
            v += 3.5
        elif (nx, ny) in unclaimed:
            v += 2.5
        elif (nx, ny) in self_set:
            v += 0.2

        adj_un = 0
        adj_opp = 0
        adj_unclaim = 0
        for ax, ay in nbs:
            tx, ty = nx + ax, ny + ay
            if not inb(tx, ty) or (tx, ty) in obstacles:
                continue
            if (tx, ty) in unclaimed:
                adj_unclaim += 1
            if (tx, ty) in opp_set:
                adj_opp += 1
            if (tx, ty) in self_set:
                adj_un += 1

        v += 0.35 * adj_unclaim
        v -= 0.45 * adj_opp
        v += 0.05 * (abs(nx - ox) + abs(ny - oy))  # prefer staying a bit away from sweeper core

        if v > bestv + 1e-9:
            bestv = v
            best = (dx, dy)

    dx, dy = best
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]