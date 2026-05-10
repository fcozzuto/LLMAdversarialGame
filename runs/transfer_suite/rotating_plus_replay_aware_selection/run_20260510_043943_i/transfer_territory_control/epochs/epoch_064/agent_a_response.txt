def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or [0, 0])
    ox, oy = map(int, observation.get("opponent_position") or [0, 0])
    turn = int(observation.get("turn_index") or 0)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_t = set()
    for p in observation.get("self_territory", []) or []:
        if p and len(p) >= 2:
            self_t.add((int(p[0]), int(p[1])))
    opp_t = set()
    for p in observation.get("opponent_territory", []) or []:
        if p and len(p) >= 2:
            opp_t.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                unclaimed.append((x, y))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if unclaimed:
        # Prefer unclaimed that we can reach earlier than opponent; tie-break by distance and turn parity.
        best = None
        for x, y in unclaimed:
            ds = abs(x - sx) + abs(y - sy)
            do = abs(x - ox) + abs(y - oy)
            score = (do - ds, -ds, -(abs(x - cx) + abs(y - cy)), (x + y + turn) % 2)
            if best is None or score > best[0]:
                best = (score, (x, y))
        tx, ty = best[1]
    else:
        # If no unclaimed, head toward opponent territory (to force flips) or center if none.
        tx, ty = ox, oy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        is_opp = (nx, ny) in opp_t
        is_self = (nx, ny) in self_t
        ds = abs(tx - nx) + abs(ty - ny)
        do = abs(tx - ox) + abs(ty - oy)
        # Encourage capturing opponent, then reducing distance to target, then moving toward center, and avoid wasting on self.
        val = 0
        val += 1000 if is_opp else 0
        val += 50 if (nx, ny) in unclaimed else 0
        val -= 3 * ds
        val += 2 if ds < abs(tx - ox) + abs(ty - oy) else 0
        val += -1 if is_self else 0
        val += -0.1 * (abs(nx - cx) + abs(ny - cy))
        val += 0.01 * ((dx + 2 * dy + turn) % 3)  # deterministic tie-break
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]