def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    my = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    un = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    opp_pos = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if (sx, sy) in obstacles:
        obstacles.discard((sx, sy))

    neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**9, 0, 0)

    # Heuristic: expand into unclaimed with strong "escape" from opponent (increase distance),
    # while blocking opponent by not entering opponent-owned cells unless it directly advances.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Base gain for claiming/expanding
        gain = 0
        if (nx, ny) in un:
            gain += 5
        if (nx, ny) in my:
            gain += 1
        if (nx, ny) in opp:
            gain -= 20  # avoid flipping if opponent has territory

        # Frontier potential: number of adjacent unclaimed cells
        adj_un = 0
        for ax, ay in neighbors:
            tx, ty = nx + ax, ny + ay
            if inside(tx, ty) and (tx, ty) in un:
                adj_un += 1
        gain += adj_un * 2

        # Opponent pressure: prefer moving away from opponent and away from their claimed cells
        dist_after = abs(nx - ox) + abs(ny - oy)
        dist_now = abs(sx - ox) + abs(sy - oy)
        escape = (dist_after - dist_now)
        gain += escape * 1.5

        # If opponent is near, strongly prefer cells that reduce their immediate capture options
        opp_adj = 0
        for ax, ay in neighbors:
            tx, ty = nx + ax, ny + ay
            if inside(tx, ty) and (tx, ty) in opp:
                opp_adj += 1
        gain -= opp_adj * 2.0

        # Deterministic tie-break: prefer staying if equal, else smallest dx, then dy
        score = int(gain * 10 + dist_after)
        if score > best[0] or (score == best[0] and (dx, dy) == (0, 0) and best[1:] != (0, 0)) or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    if best[1] is None:
        return [0, 0]
    dx, dy = best[1], best[2]
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]