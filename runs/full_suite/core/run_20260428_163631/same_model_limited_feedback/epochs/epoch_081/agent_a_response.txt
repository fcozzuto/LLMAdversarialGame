def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    self_pos = observation.get('self_position', [0, 0])
    opp_pos = observation.get('opponent_position', [7, 7])
    resources = observation.get('resources', [])
    obstacles = observation.get('obstacles', [])
    sx, sy = self_pos[0], self_pos[1]
    ox, oy = opp_pos[0], opp_pos[1]

    oxs = set((p[0], p[1]) for p in obstacles)

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy  # manhattan

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in oxs:
                moves.append((dx, dy, nx, ny))

    if not resources:
        # No resources: keep distance from opponent
        best = None
        for dx, dy, nx, ny in moves:
            dopp = dist(nx, ny, ox, oy)
            cand = (-(dopp), dx, dy)
            if best is None or cand < best[0]:
                best = (cand, [dx, dy])
        return best[1]

    # Pick a contested target: minimize (self_dist - opp_dist)
    best_r = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Bias parity to vary when tied
        parity_bias = 0 if (observation.get('turn_index', 0) % 2 == 0) else (ds - do)
        cand = (ds - do + parity_bias, ds, do, rx, ry)
        if best_r is None or cand < best_r[0]:
            best_r = (cand, (rx, ry))
    tx, ty = best_r[1]

    # Choose move that reduces distance to target and keeps away from opponent
    best = None
    for dx, dy, nx, ny in moves:
        dt = dist(nx, ny, tx, ty)
        dopp = dist(nx, ny, ox, oy)
        # Prefer farther from opponent slightly; deterministic tie-break
        cand = (dt + 0.2 * dopp, -dopp, dx, dy)
        if best is None or cand < best[0]:
            best = (cand, [dx, dy])
    return best[1]