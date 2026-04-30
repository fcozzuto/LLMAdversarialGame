def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    corner_target = (w - 1, 0) if (ox + oy) <= (sx + sy) else (0, h - 1)
    if not resources:
        tx, ty = corner_target
        best = (10**9, None)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best[0] or (d == best[0] and (dx, dy) < best[1]):
                best = (d, (dx, dy))
        return [best[1][0], best[1][1]]

    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    # If few resources remain, bias strongly to the best contested target.
    opp_bias = 0.9 if rem <= 4 else 0.45

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Base: move onto a resource if possible.
        cell_res = 1 if (nx, ny) in resources else 0
        local = 0
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach first; penalize being farther than opponent.
            contested = our_d - opp_bias * opp_d
            # Encourage reduction in distance; slight reward for being closer than now.
            now_d = cheb(sx, sy, rx, ry)
            progress = now_d - our_d
            local += (progress * 1.2) - contested * 0.8
            if (nx, ny) == (rx, ry):
                local += 50
        # Prefer getting closer while not drifting away from the board's far corner.
        local += cheb(nx, ny, ox, oy) * -0.03
        local += cell_res * (25 if rem <= 4 else 12)
        if rem <= 4:
            local += -cheb(nx, ny, corner_target[0], corner_target[1]) * 0.02
        if local > best_score or (local == best_score and (dx, dy) < best_move):
            best_score = local
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]