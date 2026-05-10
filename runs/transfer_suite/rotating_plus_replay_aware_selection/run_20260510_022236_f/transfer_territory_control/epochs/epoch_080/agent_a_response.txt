def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_score = -10**18

    candidates = unclaimed if unclaimed else list(op_terr) if op_terr else [(sx, sy)]
    for tx, ty in candidates:
        d_self = abs(tx - sx) + abs(ty - sy)
        d_opp = abs(tx - ox) + abs(ty - oy)
        # Prefer taking cells we're closer to, especially unclaimed near opponent.
        base = (d_opp - d_self)
        if (tx, ty) in unclaimed:
            base += 12
        elif (tx, ty) in op_terr:
            base += 6
        # Mild preference to avoid being trapped by obstacles: penalize targets surrounded by obstacles.
        neigh_obs = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = tx + dx, ty + dy
                if (nx, ny) in obstacles:
                    neigh_obs += 1
        score = base * 10 - d_self - neigh_obs
        if score > best_score:
            best_score = score
            best = (tx, ty)

    tx, ty = best
    # Evaluate one-step moves deterministically, with slight lookahead.
    best_move = (0, 0)
    best_move_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Immediate heuristic: prefer claiming/pressuring.
        imm = 0
        if (nx, ny) in unclaimed:
            imm += 30
        if (nx, ny) in op_terr:
            imm += 18
        if (nx, ny) in self_terr:
            imm += 2

        # Progress toward target and outpace opponent toward that same target.
        d_self = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(tx - ox) + abs(ty - oy)
        progress = (d_opp - d_self) * 3 - d_self

        # Additional bias: if opponent is closer to the target, try to reduce their lead.
        if d_self < d_opp:
            progress += 6

        score = imm + progress
        if score > best_move_score:
            best_move_score = score
            best_move = (dx, dy)

    # If all moves blocked/invalid, stay.
    if best_move == (0, 0):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]