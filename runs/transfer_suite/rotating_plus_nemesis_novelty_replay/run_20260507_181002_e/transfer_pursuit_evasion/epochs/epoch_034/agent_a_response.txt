def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    sr = str(observation.get("self_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr)

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def clamp_dir(v):
        if v > 0:
            return 1
        if v < 0:
            return -1
        return 0

    def best_opponent_move(ax, ay, tx, ty, opponent_is_evader):
        # opponent greedily maximizes distance if it's evader, else minimizes
        best = None
        for dx, dy in moves:
            nx, ny = tx + dx, ty + dy
            if not free(nx, ny):
                continue
            d = abs(nx - ax) + abs(ny - ay)
            score = d if opponent_is_evader else -d
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return (best[1], best[2]) if best else (0, 0)

    opponent_is_evader = not self_is_evader
    # If self is evader, aim to maximize distance after anticipating opponent move.
    # If self is pursuer, aim to minimize distance after anticipating opponent evasion.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # simulate opponent response from its current position
        odx, ody = best_opponent_move(nx, ny, ox, oy, opponent_is_evader)
        npx, npy = ox + odx, oy + ody
        d = abs(npx - nx) + abs(npy - ny)

        # corner/obstacle pressure: slightly prefer moves that increase min manhattan to edges when evading,
        # and prefer breaking away from corners when pursuing.
        edge_bias = min(nx, w - 1 - nx, ny, h - 1 - ny)
        pressure = (edge_bias if self_is_evader else -edge_bias) * 0.03

        # score: evader maximize, pursuer minimize
        score = (d + pressure) if self_is_evader else (-d + pressure)

        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]