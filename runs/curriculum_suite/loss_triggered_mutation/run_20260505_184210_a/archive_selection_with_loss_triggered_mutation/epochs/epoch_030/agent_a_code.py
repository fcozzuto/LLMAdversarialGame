def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        # drift toward center to reduce being corner-locked by deniers
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == cx else (1 if cx > sx else -1)
        dy = 0 if sy == cy else (1 if cy > sy else -1)
        return [dx, dy]

    # Determine contested resources: opponent currently closer than us
    contested = []
    fallback = []
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        (contested if do < ds else fallback).append((rx, ry)) if do < ds else fallback.append((rx, ry))

    target_list = contested if contested else fallback

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Primary: get closer to best contested target; Secondary: deny by choosing targets where opponent would be closer too
        if target_list:
            best_self = 10**9
            best_denier = -10**9
            for rx, ry in target_list:
                ds2 = abs(nx - rx) + abs(ny - ry)
                do2 = abs(rx - ox) + abs(ry - oy)
                if ds2 < best_self:
                    best_self = ds2
                # favor resources that opponent is likely to take quickly (high do2 disadvantage for us)
                # but we still want to be among the better reducers of those.
                best_denier = max(best_denier, do2 - ds2)
            val = -best_self + 0.15 * best_denier
        else:
            # should not happen, but safe
            val = -abs(nx - sx) - abs(ny - sy)

        # Mild separation from opponent to avoid being blocked in their denier line
        val += 0.02 * (abs(nx - ox) + abs(ny - oy))

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]