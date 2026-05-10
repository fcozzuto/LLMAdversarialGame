def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            obs.add((x, y))

    self_role = str(observation.get("self_role", "") or "")
    opponent_role = str(observation.get("opponent_role", "") or "")
    is_pursuer = ("pursuer" in self_role.lower()) or ("pursuit" in self_role.lower()) or ("hunter" in self_role.lower())
    if not is_pursuer and ("pursuer" in opponent_role.lower() or "pursuit" in opponent_role.lower()):
        is_pursuer = False
    if "evader" in self_role.lower():
        is_pursuer = False

    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    moves = []
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))
    if not moves:
        moves = [(0, 0, sx, sy)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_val = None
    for dx, dy, nx, ny in moves:
        if nx == ox and ny == oy:
            val = 10.0 if is_pursuer else -10.0
        else:
            dist = md(nx, ny, ox, oy)
            if is_pursuer:
                val = -dist
                # prefer avoiding getting "stuck" behind obstacles by mildly preferring central progress
                val -= 0.02 * md(nx, ny, w // 2, h // 2)
            else:
                val = dist
                # bias toward staying mobile / away from edges unless it increases distance to pursuer
                edge_pen = (min(nx, w - 1 - nx) + min(ny, h - 1 - ny))
                val += 0.01 * edge_pen
                # avoid moving into positions that reduce distance too much
                cur_dist = md(sx, sy, ox, oy)
                if dist < cur_dist:
                    val -= 0.05 * (cur_dist - dist)
        if best is None or (val > best_val) or (val == best_val and (dx, dy) < (best[0], best[1])):
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]