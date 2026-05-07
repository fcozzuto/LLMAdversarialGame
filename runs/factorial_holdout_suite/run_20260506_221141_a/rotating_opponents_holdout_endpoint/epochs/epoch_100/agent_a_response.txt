def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose a target where we arrive not later than opponent; tie-break by closeness and parity.
    best = None
    best_key = None
    for tx, ty in resources:
        sdist = cheb(sx, sy, tx, ty)
        odist = cheb(ox, oy, tx, ty)
        lead = odist - sdist
        key = (lead, -sdist, -((tx + ty) & 1), -(tx * 17 + ty * 31))
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, cheb(nx, ny, tx, ty)))

    # Allow staying still if all moves are blocked or worse than current.
    cur_d = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_val = cur_d

    for dx, dy, d in moves:
        val = d
        if val < best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # Deterministic tie-break: closer to opponent too (to deny), then lower dx/dy order.
            nd_opp = cheb(sx + dx, sy + dy, ox, oy)
            nbest_opp = cheb(sx + best_move[0], sy + best_move[1], ox, oy)
            if nd_opp < nbest_opp or (nd_opp == nbest_opp and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]