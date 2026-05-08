def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_heuristic(px, py):
        best = (-10**9, 10**9)
        for rx, ry in resources:
            self_d = man(px, py, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            if self_d == 0:
                return (10**9, 0)
            # Prefer positions where we are relatively closer than opponent.
            rel = (opp_d - self_d)
            cand = (rel, self_d)
            if cand > best:
                best = cand
        return best

    best_move = (0, 0)
    best_val = (-10**18, 10**9)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        h1 = best_heuristic(nx, ny)
        # 1-step lookahead: after we move, choose our next greedy action; opponent static in heuristic (deterministic, cheap).
        h2 = (-10**9, 10**9)
        for ddx, ddy in moves:
            nnx, nny = nx + ddx, ny + ddy
            if not (0 <= nnx < w and 0 <= nny < h) or (nnx, nny) in obs:
                continue
            cand = best_heuristic(nnx, nny)
            if cand > h2:
                h2 = cand
        val = (h1[0] * 2 + h2[0], min(h1[1], h2[1]))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]