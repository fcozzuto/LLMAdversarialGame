def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chaser" in self_role) or ("tag" in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Predict opponent next position by assuming they move greedily
    # - if we are pursuer, they likely evade => maximize distance
    # - if we are evader, they likely pursue => minimize distance
    def predict_opp_next():
        best = None
        best_val = None
        for dx, dy in deltas:
            nx, ny = ox + dx, oy + dy
            if not clamp_in(nx, ny) or (nx, ny) in obst:
                continue
            d = dist2(nx, ny, sx, sy)
            val = d if not is_pursuer else -d
            if best is None or val > best_val:
                best = (dx, dy)
                best_val = val
        if best is None:
            return (ox, oy)
        return (ox + best[0], oy + best[1])

    po_x, po_y = predict_opp_next()

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            continue
        if (nx, ny) in obst:
            continue

        d_now = dist2(nx, ny, ox, oy)
        d_pred = dist2(nx, ny, po_x, po_y)

        # Obstacle avoidance: discourage moving adjacent to obstacles more when evading
        adj_pen = 0
        for ax, ay in obst:
            dd = dist2(nx, ny, ax, ay)
            if dd == 1:
                adj_pen += 1
            elif dd == 0:
                adj_pen += 10

        if is_pursuer:
            # Seek capture quickly: reduce distance to predicted next evader position
            score = -0.85 * d_pred - 0.15 * d_now - 3.0 * adj_pen
        else:
            # Evade: maximize distance from predicted pursuer next position
            score = 0.9 * d_pred + 0.1 * d_now - 2.5 * adj_pen

        # Deterministic tiebreaker: prefer smaller |dx|+|dy|, then lexicographic
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            cand = abs(dx) + abs(dy)
            cur = abs(best_move[0]) + abs(best_move[1])
            if cand < cur or (cand == cur and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]