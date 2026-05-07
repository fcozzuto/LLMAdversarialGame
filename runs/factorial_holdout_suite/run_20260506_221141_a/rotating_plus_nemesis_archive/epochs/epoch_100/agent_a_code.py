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

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]
    if not resources:
        tx = 0 if sx > w - 1 - sx else w - 1
        ty = 0 if sy > h - 1 - sy else h - 1
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer moves that put you closer to a resource than the opponent is (race heuristic).
    # Also prefer reducing your distance to the currently best "lead" target.
    best_move = moves[0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        corner_bias = -((nx - 0) * (nx - 0) + (ny - 0) * (ny - 0)) * 0.0001
        corner_bias += -((nx - (w - 1)) * (nx - (w - 1)) + (ny - (h - 1)) * (ny - (h - 1))) * 0.0001
        local_best = -10**18
        for rx, ry in resources:
            sd = abs(rx - nx) + abs(ry - ny)
            od = abs(rx - ox) + abs(ry - oy)
            # If you can reach immediately, take it.
            if sd == 0:
                lead = 10**9
            else:
                lead = (od - sd) * 100 - sd
            # Small obstacle-avoidance: discourage stepping near obstacles.
            adj_obs = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    px, py = nx + ax, ny + ay
                    if 0 <= px < w and 0 <= py < h and (px, py) in obstacles:
                        adj_obs += 1
            val = lead - adj_obs * 3
            if val > local_best:
                local_best = val
        val = local_best + corner_bias
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]