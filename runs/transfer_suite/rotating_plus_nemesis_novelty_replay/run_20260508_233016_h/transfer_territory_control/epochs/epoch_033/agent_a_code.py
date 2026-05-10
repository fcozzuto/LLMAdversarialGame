def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_pos = tuple(observation["opponent_position"])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    yield nx, ny

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target: prioritize unclaimed cells that are close to opponent territory; else closest unclaimed.
    unclaimed_list = list(unclaimed)
    best_target = None
    best_tscore = -10**18
    if unclaimed_list:
        for ux, uy in unclaimed_list:
            d_opp = man(ux, uy, opp_pos[0], opp_pos[1])
            near_opp_border = 0
            for nx, ny in neighbors8(ux, uy):
                if (nx, ny) in opp_terr:
                    near_opp_border = 1
                    break
            tscore = (10.0 if near_opp_border else 0.0) - 0.25 * d_opp - 0.02 * man(sx, sy, ux, uy)
            if tscore > best_tscore:
                best_tscore = tscore
                best_target = (ux, uy)

    if best_target is None:
        best_target = (w // 2, h // 2)

    tx, ty = best_target

    # Evaluate one-step moves: counterclaim pressure + obstacle safety + avoid moving into opponent far from flip value.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        val = 0.0
        if cell in unclaimed:
            val += 6.0
        if cell in self_terr:
            val -= 0.2
        if cell in opp_terr:
            val += 5.0  # flipping on entry
        # If stepping close to opponent territory, boost (build counterclaim lines).
        border_adj = 0
        for ax, ay in neighbors8(nx, ny):
            if (ax, ay) in opp_terr:
                border_adj = 1
                break
        if border_adj:
            val += 2.5

        # Prefer moving toward target, but still allow counterclaim even if slightly farther.
        val += 1.0 * (-man(nx, ny, tx, ty))
        # Mildly avoid getting too close to opponent position unless we can claim/flip.
        d_to_opp = man(nx, ny, opp_pos[0], opp_pos[1])
        if d_to_opp <= 1 and (cell not in unclaimed) and (cell not in opp_terr):
            val -= 1.5

        # Deterministic tie-breaker: prefer staying still last, then lexicographic order.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]