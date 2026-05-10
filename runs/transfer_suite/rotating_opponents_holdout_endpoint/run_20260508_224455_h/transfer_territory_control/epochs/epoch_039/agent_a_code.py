def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for c in observation.get("obstacles", []) or []:
        obstacles.add((int(c[0]), int(c[1])))

    self_cells = set()
    for c in observation.get("self_territory", []) or []:
        self_cells.add((int(c[0]), int(c[1])))

    opp_cells = set()
    for c in observation.get("opponent_territory", []) or []:
        opp_cells.add((int(c[0]), int(c[1])))

    unclaimed = observation.get("unclaimed_cells", []) or []
    unclaimed_cells = [(int(c[0]), int(c[1])) for c in unclaimed]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_to(a_set, x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in a_set:
                    return True
        return False

    tx, ty = int(round(cx)), int(round(cy))
    if unclaimed_cells:
        best = None
        for x, y in unclaimed_cells:
            d = abs(x - sx) + abs(y - sy)
            adj_self = 1 if adj_to(self_cells, x, y) else 0
            adj_opp = 1 if adj_to(opp_cells, x, y) else 0
            val = (d, -adj_self, -adj_opp, x, y)
            if best is None or val < best[0]:
                best = (val, (x, y))
        tx, ty = best[1]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def move_val(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        base = - (abs(nx - tx) + abs(ny - ty))
        if (nx, ny) in opp_cells:
            base += 80  # counterclaim quickly
        elif (nx, ny) in self_cells:
            base += 10
        else:
            base += 15 if (nx, ny) not in self_cells and (nx, ny) not in opp_cells else 0
        base += -0.01 * (abs(nx - (w - 1)) + abs(ny - (h - 1)) if sy <= (h - 1) / 2 else abs(nx) + abs(ny))
        return base

    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = move_val(nx, ny)
        if best_score is None or sc > best_score:
            best_score = sc
            best_move = [dx, dy]
        elif sc == best_score:
            if [dx, dy] < best_move:
                best_move = [dx, dy]
    return best_move