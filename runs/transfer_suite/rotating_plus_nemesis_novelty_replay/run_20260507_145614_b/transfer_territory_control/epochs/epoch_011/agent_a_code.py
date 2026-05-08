def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    opp = observation.get("opponent_position")
    oppx, oppy = opp if opp else (sx, sy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y):
                obs.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    targets = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs:
                targets.append((x, y))
    if not targets:
        for p in observation.get("opponent_territory") or []:
            if p and len(p) >= 2:
                x, y = p[0], p[1]
                if inb(x, y) and (x, y) not in obs:
                    targets.append((x, y))
    if not targets:
        targets = [(oppx, oppy)]

    tx, ty = min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist_t = abs(tx - nx) + abs(ty - ny)
        dist_o = abs(oppx - nx) + abs(oppy - ny)
        val = -dist_t + 0.05 * dist_o
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]