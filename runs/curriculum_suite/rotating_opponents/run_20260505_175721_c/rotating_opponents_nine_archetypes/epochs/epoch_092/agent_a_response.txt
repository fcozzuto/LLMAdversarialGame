def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Strategy: choose move maximizing immediate capture advantage over opponent on some resource.
    # Advantage = (opp_dist - self_dist); also lightly prefer moving closer to the chosen resource.
    best_move = (0, 0)
    best_score = -10**18
    best_res = resources[0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        local_best = -10**18
        local_res = resources[0]
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            # Prefer taking lead strongly; if tied, prefer shorter self distance; deterministic tie by coords.
            val = adv * 1000 - sd
            if val > local_best or (val == local_best and (rx, ry) < local_res):
                local_best = val
                local_res = (rx, ry)
        # Break ties between moves by: higher best advantage, then closer to the move's selected resource, then lexicographic.
        sd_sel = cheb(nx, ny, local_res[0], local_res[1])
        if (local_best > best_score or
            (local_best == best_score and (sd_sel < cheb(sx, sy, best_res[0], best_res[1]) or
             (sd_sel == cheb(sx, sy, best_res[0], best_res[1]) and (dx, dy) < best_move)))):
            best_score = local_best
            best_move = (dx, dy)
            best_res = local_res

    return [int(best_move[0]), int(best_move[1])]