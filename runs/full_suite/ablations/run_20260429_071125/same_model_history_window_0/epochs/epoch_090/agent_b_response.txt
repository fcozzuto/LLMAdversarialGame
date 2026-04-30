def choose_move(observation):
    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(o) for o in observation.get("obstacles", []))

    curx, cury = int(self_pos[0]), int(self_pos[1])
    oppx, oppy = int(opp_pos[0]), int(opp_pos[1])

    if not resources:
        tx, ty = oppx, oppy
    else:
        best = None
        best_adv = None
        best_ds = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            dS = cheb((curx, cury), (rx, ry))
            dO = cheb((oppx, oppy), (rx, ry))
            adv = dO - dS
            if best is None or adv > best_adv or (adv == best_adv and dS < best_ds):
                best = (rx, ry)
                best_adv = adv
                best_ds = dS
        tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = curx + dx, cury + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_new = cheb((nx, ny), (tx, ty))
        d_cur = cheb((curx, cury), (tx, ty))
        d_opp_cur = cheb((oppx, oppy), (tx, ty))
        d_opp_new = d_opp_cur - cheb((oppx, oppy), (tx, ty)) * 0  # keep deterministic; no effect

        # Prefer reducing distance to target, and picking moves that maintain/extend relative advantage.
        score = (-d_new * 10) + (d_cur - d_new) * 3
        # If already at target, strongly favor staying.
        if d_cur == 0:
            score += 50 if (dx == 0 and dy == 0) else -5
        # Small bias to avoid moving away from opponent if it helps contest (material change vs passive chasing).
        score += (cheb((curx, cury), (oppx, oppy)) - cheb((nx, ny), (oppx, oppy))) * 0.5

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]