def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # Deny by moving toward center between agents; also steer slightly away from opponent if close.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        tx = cx + (sx - ox) * 0.25
        ty = cy + (sy - oy) * 0.25
        bestd = 10**9
        bestm = [0, 0]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in obs: 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                bestm = [dx, dy]
        return bestm

    # Pick target deterministically: prefer where we are no farther than opponent; then minimize our distance; then tie-break by coord.
    best_target = None
    best_key = None
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        advantage = md - od  # <=0 good
        key = (0 if advantage <= 0 else 1, md, -rx, -ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target
    best_score = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obs:
            continue
        # One-step look: minimize our distance to target, but also prevent opponent from getting much closer.
        md = cheb(nx, ny, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Convert to advantage score: higher is better.
        adv = (od - md)  # positive means we are closer than opponent
        # Secondary: avoid giving opponent a closer route to the same target by moving into their vicinity.
        opp_prox = cheb(nx, ny, ox, oy)
        # Tertiary: keep away from obstacles slightly by biasing toward open cells.
        neigh_block = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                tx, ty = nx + adx, ny + ady
                if (tx, ty) in obs:
                    neigh_block += 1
        score = (adv * 1000) + (-md * 10) + (-opp_prox) + (-neigh_block * 2) + (-abs(nx - rx) - abs(ny - ry))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move