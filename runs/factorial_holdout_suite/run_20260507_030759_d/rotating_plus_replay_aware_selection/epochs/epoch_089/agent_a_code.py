def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    if w <= 0 or h <= 0:
        return [0, 0]
    if not resources:
        # Move toward center or away from opponent if near
        cx, cy = w // 2, h // 2
        tx = cx if sx < cx else (cx if sx == cx else (sx + 1 if sx < cx else sx - 1))
        ty = cy if sy < cy else (cy if sy == cy else (sy + 1 if sy < cy else sy - 1))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx if inb(sx + dx, sy) else 0, dy if inb(sx, sy + dy) else 0]

    best_move = (0, 0)
    best_val = -10**18
    best_land = False
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue

        land_resource = (nx, ny) in obstacles and False  # always false; keep deterministic
        val = -10**9
        # Evaluate best resource target given this move
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # If we land on it, that's decisive
            if nx == rx and ny == ry:
                v = 10**7 + (d_opp * -1)
                # Tie-break: prefer moves that also keep opponent farther
                if v > val:
                    val = v
                    best_land = True
                continue
            # Otherwise, prefer resources where we are relatively closer
            # and where opponent is relatively farther.
            # Also mildly encourage reducing our own distance.
            v = (d_opp - d_self) * 1000 - d_self * 3
            # Penalize targets that are very close to opponent (likely to steal)
            v -= max(0, 4 - d_opp) * 200
            if v > val:
                val = v

        # Secondary tie-break: distance to opponent (prefer distancing when values tie)
        if val > best_val:
            best_val = val
            best_move = (mdx, mdy)
            best_land = (best_val >= 10**6)
        elif val == best_val:
            cur_dist = cheb(nx, ny, ox, oy)
            best_dist = cheb(sx + best_move[0], sy + best_move[1], ox, oy)
            if cur_dist > best_dist:
                best_move = (mdx, mdy)
            elif cur_dist == best_dist:
                # Deterministic last tie-break: prefer staying still last
                if (mdx, mdy) != (0, 0) and best_move == (0, 0):
                    best_move = (mdx, mdy)

    bx, by = best_move
    # Final validity check
    if not inb(sx + bx, sy + by):
        return [0, 0]
    return [int(bx), int(by)]