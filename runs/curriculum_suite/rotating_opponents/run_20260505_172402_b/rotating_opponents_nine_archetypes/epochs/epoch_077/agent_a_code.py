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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Corner-guard opponent: keep moving along a safe "wall" direction
        tx = 1 if ox == w - 1 else w - 2 if ox == 0 else (w - 1) // 2
        ty = 1 if oy == h - 1 else h - 2 if oy == 0 else (h - 1) // 2
        resources = [(tx, ty)]

    # Pick best resource deterministically: closest, then lower x, then lower y
    best_r = None
    best_d = 10**9
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if d < best_d or (d == best_d and (rx < best_r[0] or (rx == best_r[0] and ry < best_r[1]))):
            best_d = d
            best_r = (rx, ry)

    rx, ry = best_r
    # Evaluate next moves: approach resource, avoid obstacles already handled, and avoid opponent proximity
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_res = cheb(nx, ny, rx, ry)
        # Prefer reducing distance; slight bias to move toward target cell axes for determinism
        res_score = -d_res * 100 - abs(nx - rx) - abs(ny - ry)
        d_opp = cheb(nx, ny, ox, oy)
        # Penalize getting too close to opponent (corner_guard style)
        opp_pen = 0
        if d_opp <= 2:
            opp_pen = (3 - d_opp) * 250
        elif d_opp <= 3:
            opp_pen = (4 - d_opp) * 80
        score = res_score - opp_pen
        # Deterministic tie-break: prefer moves in fixed order list
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]