def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    opT = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opT.add((int(p[0]), int(p[1])))

    unT = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unT.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def count_adj(cell, S):
        x, y = cell
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in S:
                    c += 1
        return c

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        cell = (nx, ny)
        adj_un = count_adj(cell, unT)
        adj_self = count_adj(cell, selfT)
        adj_op = count_adj(cell, opT)

        if cell in opT:
            val = 6.0 + 0.6 * adj_un + 0.2 * adj_self - 0.1 * adj_op
        elif cell in unT:
            val = 3.5 + 0.9 * adj_self + 0.4 * adj_un - 0.2 * adj_op
        elif cell in selfT:
            val = 1.5 + 0.7 * adj_un - 0.1 * adj_op
        else:
            val = 0.2 + 0.2 * adj_un - 0.05 * adj_op

        if val > best[0]:
            best = (val, dx, dy)
    return [int(best[1]), int(best[2])]