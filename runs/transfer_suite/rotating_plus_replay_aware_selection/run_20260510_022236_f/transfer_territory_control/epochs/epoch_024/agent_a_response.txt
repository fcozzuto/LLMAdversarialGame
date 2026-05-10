def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                unclaimed.append((x, y))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    opp_pos = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    cx, cy = w // 2, h // 2

    if not unclaimed:
        return [0, 0]

    if not self_terr:
        targets = unclaimed
    else:
        our_front = set()
        for (x, y) in self_terr:
            for dx, dy in dirs8:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) in set(unclaimed):
                    our_front.add((nx, ny))
        targets = list(our_front) if our_front else unclaimed

    set_un = set(unclaimed)

    best = None
    best_score = None
    parity = int(observation.get("turn_index", 0) or 0) & 1

    for tx, ty in targets:
        if (tx, ty) not in set_un or (tx, ty) in obstacles:
            continue
        dcenter = abs(tx - cx) + abs(ty - cy)
        dopp = abs(tx - ox) + abs(ty - oy)
        # Frontier preference: keep expanding, but prioritize center and avoid opponent-owned traps
        near_opp = 1 if any((nx, ny) in opp_terr for nx in (tx - 1, tx, tx + 1) for ny in (ty - 1, ty, ty + 1) if inb(nx, ny)) else 0
        border_bias = 1 if (tx in (0, w - 1) or ty in (0, h - 1)) else 0
        score = (-2 * dcenter) + (1.2 * dopp) - (3.5 * near_opp) - (1.2 * border_bias) + (0.01 * ((tx + ty) + parity))
        if best_score is None or score > best_score:
            best_score = score
            best = (tx, ty)

    tx, ty = best

    # Choose a legal move that reduces distance to target; deterministic tie-break by dir order.
    best_move = (0, 0)
    best_dist = None
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        if best_dist is None or dist < best_dist or (dist == best_dist and (dx, dy) != best_move):
            best_dist = dist
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]