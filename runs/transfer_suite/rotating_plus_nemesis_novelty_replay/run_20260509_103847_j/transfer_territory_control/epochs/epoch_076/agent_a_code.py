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
            nx = x + dx
            if nx < 0 or nx >= w:
                continue
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ny = y + dy
                if 0 <= ny < h and (nx, ny) in S:
                    c += 1
        return c

    # opponent position as distance anchor (fewer computations than scanning opT)
    op_pos = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(op_pos[0]), int(op_pos[1])

    best_move = [0, 0]
    best_score = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue

            is_un = (nx, ny) in unT
            is_self = (nx, ny) in selfT
            is_op = (nx, ny) in opT

            # Avoid getting swept: prefer advancing where opponent is farther away, and keep near our territory.
            dist_op = abs(nx - ox) + abs(ny - oy)
            score = 0.0
            if is_un:
                score += 3.0
            elif is_op:
                score += 1.2  # flipping can help, but don't overcommit into their path
            elif is_self:
                score += 0.6
            score += 0.9 * adj_count((nx, ny), selfT)
            score -= 0.7 * adj_count((nx, ny), opT)
            score += 0.04 * dist_op

            # Prefer moves that increase distance from edges only when safe (territory_sweeper tends to hug edges).
            edge_pen = 0
            if nx in (0, w - 1) or ny in (0, h - 1):
                edge_pen = 0.15
            score -= edge_pen

            if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
                best_score = score
                best_move = [dx, dy]
    return best_move