def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    cand_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            cand_moves.append((dx, dy, nx, ny))
    if not cand_moves:
        return [0, 0]

    # Target selection for a position: best resource by advantage (opponent closer is bad).
    # Also prefer resources not too close to opponent.
    def best_target_from(px, py):
        best = None
        for r in resources:
            if not r or len(r) != 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not inside(rx, ry):
                continue
            myd = cheb(px, py, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # want bigger
            # Penalize resources the opponent can reach very quickly.
            tpen = 0 if opd >= 3 else (3 - opd) * 1.25
            key = (-adv, myd + tpen, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry, myd, opd, adv)
        return best

    best_overall = None
    # Evaluate each candidate move by the best target it could secure next.
    for dx, dy, nx, ny in cand_moves:
        bt = best_target_from(nx, ny)
        if bt is None:
            # No valid resources; fall back to move that maximizes distance from opponent.
            key = (cheb(nx, ny, ox, oy), nx, ny)
            cand_key = (key[0], key[1], key[2])
            if best_overall is None or cand_key < best_overall[0]:
                best_overall = (cand_key, dx, dy)
            continue
        _, rx, ry, myd, opd, adv = bt
        # Prefer moves that improve advantage and increase distance from opponent to the chosen target.
        # Deterministic tie-break by coordinates.
        dist_to_target = myd
        opp_to_target = opd
        immediate = -adv * 2.0 + (2.0 - dist_to_target) * 0.6 + (opp_to_target - dist_to_target) * 0.3
        # Higher immediate is better -> convert to minimize.
        cand_key = (-immediate, dist_to_target, opp_to_target, rx, ry, nx, ny)
        if best_overall is None or cand_key < best_overall[0]:
            best_overall = (cand_key, dx, dy)

    return [int(best_overall[1]), int(best_overall[2])]