def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    if not resources:
        # With no visible resources, maximize distance from opponent.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                val = -10**9
            else:
                val = cheb(nx, ny, ox, oy)
            if val > best_val:
                best_val, best_move = val, (dx, dy)
        return [best_move[0], best_move[1]]

    # Precompute opponent's best distance to any resource.
    opp_best = min(cheb(ox, oy, rx, ry) for rx, ry in resources)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            val = -10**12
        else:
            if (nx, ny) in res_set:
                val = 10**9
            else:
                my_best = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
                # If we are closer than opponent to at least one resource, prefer it.
                # Also prefer increasing separation from opponent.
                sep = cheb(nx, ny, ox, oy)
                val = 0
                val -= my_best * 20
                val += sep * 3
                if my_best < opp_best:
                    val += (opp_best - my_best) * 35
                # Small deterministic nudge to prefer not drifting directly toward opponent.
                # (Try to keep moves that increase x+y parity alignment away from opponent.)
                val += (0 if (nx + ny) % 2 == (ox + oy) % 2 else 1)
        if val > best_val:
            best_val, best_move = val, (dx, dy)

    return [best_move[0], best_move[1]]