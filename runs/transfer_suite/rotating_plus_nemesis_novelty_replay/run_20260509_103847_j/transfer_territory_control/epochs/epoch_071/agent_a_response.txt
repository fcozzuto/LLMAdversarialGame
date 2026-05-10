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

    def adj_count(cell, S):
        x, y = cell
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in S:
                    c += 1
        return c

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ti = int(observation.get("turn_index", 0))
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        is_self = (nx, ny) in selfT
        is_op = (nx, ny) in opT
        is_un = (nx, ny) in unT

        score = 0
        if is_self:
            score += 1
        if is_un:
            score += 3 + adj_count((nx, ny), selfT)
        if is_op:
            score += 6 + adj_count((nx, ny), selfT)
            score += 1 if adj_count((nx, ny), opT) > 0 else 0

        score += 0.5 * adj_count((nx, ny), unT)
        score += 0.2 * (adj_count((nx, ny), selfT) - adj_count((nx, ny), opT))

        # deterministic tie-breaker to reduce dithering
        score += (0.01 if ((nx + ny + ti) & 1) == 0 else 0.0)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move