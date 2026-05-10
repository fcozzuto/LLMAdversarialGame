def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    unclaimed = [(int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or [])]
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_count(cellset, x, y):
        c = 0
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in cellset:
                c += 1
        return c

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    candidates = unclaimed if unclaimed else list(opp_terr)
    best_cell = None
    best_val = -10**18
    for x, y in candidates:
        if (x, y) in obstacles or not inb(x, y):
            continue
        d = dist_cheb(sx, sy, x, y)
        if d == 0:
            continue
        a_self = adj_count(self_terr, x, y)
        a_opp = adj_count(opp_terr, x, y)
        # Prefer expansion from our border; avoid getting boxed near opponent.
        val = (3 * a_self) - (2 * a_opp) - d
        if val > best_val:
            best_val = val
            best_cell = (x, y)

    if best_cell is None:
        return [0, 0]

    tx, ty = best_cell
    # Choose move that gets closest to target (with obstacle avoidance), deterministically tie-break.
    best_move = (0, 0)
    best_d = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = dist_cheb(nx, ny, tx, ty)
        if d < best_d:
            best_d = d
            best_move = (dx, dy)
        elif d == best_d:
            # deterministic tie-break: prefer diagonals, then right, then up, then stay
            key = (0 if (dx != 0 and dy != 0) else 1, -dx, -dy, 0 if (dx == 0 and dy == 0) else 1)
            cur = (0 if (best_move[0] != 0 and best_move[1] != 0) else 1, -best_move[0], -best_move[1], 0 if (best_move[0] == 0 and best_move[1] == 0) else 1)
            if key < cur:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]