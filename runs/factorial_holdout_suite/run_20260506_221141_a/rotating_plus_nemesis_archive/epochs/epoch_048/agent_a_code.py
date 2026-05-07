def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def clamp(a, lo, hi):
        if a < lo: return lo
        if a > hi: return hi
        return a

    def d_self(x, y):
        return abs(x - sx) + abs(y - sy)

    def d_opp(x, y):
        return abs(x - ox) + abs(y - oy)

    if not resources:
        # drift to center while avoiding immediate obstacles
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    prefer_not_row = (sy == oy)
    best_res = None
    best_score = None
    for (rx, ry) in resources:
        if prefer_not_row and ry == oy and len(resources) > 1:
            continue
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        # higher is better: win race (opp closer => worse), then closer to self, then deterministic bias
        parity_bias = ((rx + ry) & 1) * 0.001
        score = ((od - sd), (-sd), parity_bias)
        if best_score is None or score > best_score:
            best_score = score
            best_res = (rx, ry)

    rx, ry = best_res
    # Choose the move that maximizes the race advantage for the chosen target; if tied, avoid obstacles and drift away from opponent
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = abs(rx - nx) + abs(ry - ny)
        nod = abs(rx - ox) + abs(ry - oy)
        # also consider increasing distance from opponent when resources are tied
        opp_spread = abs(nx - ox) + abs(ny - oy)
        val = ((nod - nsd), (-nsd), opp_spread)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]