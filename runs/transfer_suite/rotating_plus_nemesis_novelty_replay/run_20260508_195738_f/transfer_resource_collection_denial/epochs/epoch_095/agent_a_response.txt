def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    ti = int(observation.get("turn_index", 0) or 0)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            resources.append((int(r[0]), int(r[1])))
        except Exception:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Determine target: prioritize resources where we arrive sooner; tie-break by distance and safety from opponent
    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Higher score advantage for us; also slightly prefer nearer resources and avoid where opponent is much closer
            val = (do - ds) * 1000 + (20 - ds) * 3 - (abs(rx - ox) + abs(ry - oy)) * 0.01
            # Deterministic tie-break
            tie = (-ds, -cheb(ox, oy, rx, ry), rx * 8 + ry)
            cand = (val, tie, (rx, ry))
            if best is None or cand > best:
                best = cand
        tx, ty = best[2]
    else:
        # No visible resources: go to a corner closest to the opponent parity to keep pressure
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        idx = ((ox + oy + ti) & 3)
        tx, ty = corners[idx]

    # Choose best single-step move toward target, avoiding obstacles; if blocked, still move toward target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            # Strongly discourage stepping into known obstacles, but keep option if all are blocked
            obs_pen = 10000
        else:
            obs_pen = 0

        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Encourage reducing our distance to target; keep some spacing from opponent
        score = obs_pen + d_to * 10 - d_opp * 0.2 + (dx * 0.01 + dy * 0.02)
        cand = (score, dx, dy)
        if best_score is None or cand < best_score:
            best_score = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]