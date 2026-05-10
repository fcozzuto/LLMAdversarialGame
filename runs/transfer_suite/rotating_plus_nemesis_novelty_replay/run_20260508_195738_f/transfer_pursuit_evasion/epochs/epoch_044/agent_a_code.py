def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Greedy opponent: after our move, it moves to minimize distance to us.
    def opp_step(px, py, tx, ty):
        best = None
        bestd = None
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not ok(nx, ny):
                nx, ny = px, py
            d = dist2(nx, ny, tx, ty)
            if best is None or d < bestd:
                bestd = d
                best = (nx, ny)
        return best

    best_move = (0, 0)
    best_score = None

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not ok(nx, ny):
            nx, ny = sx, sy

        # If we would be captured immediately (capture radius 0), avoid it.
        if nx == ox and ny == oy:
            continue

        enx, eny = opp_step(ox, oy, nx, ny)

        # Score: maximize distance after both move (evade pursuer).
        score = dist2(nx, ny, enx, eny)

        # Small deterministic obstacle-safety: prefer being not adjacent to obstacles.
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs:
                    adj += 1
        score -= 0.5 * adj

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]