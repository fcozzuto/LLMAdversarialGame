def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    cx, cy = w // 2, h // 2
    target = None
    best = 10**18

    un_list = list(unT)
    if not un_list:
        un_list = list(opT)  # as fallback, try to press opponent territory
    if un_list:
        for tx, ty in un_list:
            tx, ty = int(tx), int(ty)
            if (tx, ty) in obs:
                continue
            ds = abs(sx - tx) + abs(sy - ty)
            do = abs(ox - tx) + abs(oy - ty)
            center = abs(tx - cx) + abs(ty - cy)
            # Deny opponent by preferring cells far from opponent, reachable by us, and toward the center.
            cell_val = ds + 0.55 * do - 0.35 * center
            # If cell is adjacent to our territory, weight it slightly higher for smoother expansion.
            if ((tx, ty) in selfT) or (abs(tx - sx) <= 1 and abs(ty - sy) <= 1):
                cell_val -= 0.15
            # Prefer taking unclaimed over contesting if possible.
            if (tx, ty) in unT:
                cell_val -= 0.25
            if cell_val < best:
                best = cell_val
                target = (tx, ty)

    if target is None:
        return [0, 0]

    tx, ty = target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_d = 10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        # Slightly avoid moving into cells that opponent already owns (flipping is allowed but risky).
        if (nx, ny) in opT:
            d += 0.15
        # Prefer extending in the direction away from opponent.
        if do := (abs(nx - ox) + abs(ny - oy)):
            d -= 0.02 * do
        if d < best_d:
            best_d = d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]