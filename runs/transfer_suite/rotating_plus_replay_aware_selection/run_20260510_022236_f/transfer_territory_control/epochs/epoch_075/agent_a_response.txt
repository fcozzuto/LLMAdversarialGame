def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]
    if not unclaimed:
        return [0, 0]

    up = int(observation.get("self_territory_count") or len(self_terr))
    op = int(observation.get("opponent_territory_count") or len(op_terr))
    we_lead = up >= op

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh4(x, y):
        return ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))

    def adj_to_our(c):
        x, y = c
        for nx, ny in neigh4(x, y):
            if (nx, ny) in self_terr:
                return True
        return False

    def adj_to_op(c):
        x, y = c
        for nx, ny in neigh4(x, y):
            if (nx, ny) in op_terr:
                return True
        return False

    # Pick a deterministic target
    best = None
    best_key = None
    for c in unclaimed:
        x, y = c
        d = abs(x - sx) + abs(y - sy)
        if we_lead:
            pr = 0 if adj_to_our(c) else 1
        else:
            pr = 0 if adj_to_op(c) else (1 if adj_to_our(c) else 2)
        # tie-break deterministically by coordinates
        key = (pr, d, y, x)
        if best_key is None or key < best_key:
            best_key = key
            best = c
    tx, ty = best

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Lower distance to target is better; landing on valuable cells is better.
        dist = abs(tx - nx) + abs(ty - ny)
        land = 0
        if (nx, ny) in unclaimed:
            land += 6
            if (not we_lead) and adj_to_op((nx, ny)):
                land += 4
        if (nx, ny) in op_terr:
            land += 7 if not we_lead else 5
        if (nx, ny) in self_terr:
            land += 1
        # Prefer moves that don't step backward too much in pursuit.
        prog = abs(tx - sx) + abs(ty - sy) - dist
        score = (-(dist * 10) - land - (prog < 0) * 3)  # more is better after inversion style
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]