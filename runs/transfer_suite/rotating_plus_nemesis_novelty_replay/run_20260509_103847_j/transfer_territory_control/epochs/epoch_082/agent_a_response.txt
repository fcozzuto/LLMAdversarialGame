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

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(ox), int(oy)

    opp_centre = (w // 2, h // 2)
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        cell = (nx, ny)
        base = 0
        if cell in opT:
            base = 8
        elif cell in unT:
            base = 4
        elif cell in selfT:
            base = 1
        else:
            base = -2

        adj_self = 0
        adj_un = 0
        adj_op = 0
        for ax, ay in neighbors8(nx, ny):
            if (ax, ay) in selfT:
                adj_self += 1
            elif (ax, ay) in unT:
                adj_un += 1
            elif (ax, ay) in opT:
                adj_op += 1

        dist_to_opp = manh((nx, ny), (ox, oy))
        dist_to_centre = manh((nx, ny), opp_centre)

        # Prefer expanding contact with our territory; also bias toward breaking into opponent-held cells.
        score = base + 2 * adj_self + 1 * adj_un + 3 * adj_op - 0.03 * dist_to_opp - 0.01 * dist_to_centre

        if best is None or score > best or (score == best and (dx, dy) < best_move):
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]