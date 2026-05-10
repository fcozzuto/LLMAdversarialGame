def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obstacles.add((int(q[0]), int(q[1])))
            elif "x" in p and "y" in p:
                obstacles.add((int(p["x"]), int(p["y"])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                resources.append((int(q[0]), int(q[1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))

    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy  # Chebyshev (diagonal moves)

    best_target = None
    best_adv = None
    for rx, ry in resources:
        adv = dist(sx, sy, rx, ry) - dist(ox, oy, rx, ry)  # negative => we are closer
        if best_target is None or adv < best_adv or (adv == best_adv and dist(sx, sy, rx, ry) < dist(sx, sy, best_target[0], best_target[1])):
            best_target = (rx, ry)
            best_adv = adv

    if best_target is None:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    tx, ty = best_target

    # Opponent pressure: if we can't secure, move to reduce their access by aiming for their best alternative too.
    opp_best = None
    opp_best_d = None
    for rx, ry in resources:
        d = dist(ox, oy, rx, ry)
        if opp_best is None or d < opp_best_d or (d == opp_best_d and dist(sx, sy, rx, ry) < dist(sx, sy, opp_best[0], opp_best[1])):
            opp_best = (rx, ry)
            opp_best_d = d
    pbx, pby = opp_best if opp_best is not None else (tx, ty)

    best_score = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            nx, ny = sx, sy
        hit = (nx, ny) in obstacles
        # Higher is better
        our_d = dist(nx, ny, tx, ty)
        opp_d = dist(nx, ny, pbx, pby)
        opp_access = dist(ox, oy, tx, ty)
        score = -our_d
        score += 0.35 * (opp_best_d - dist(ox, oy, pbx, pby))  # small deterministic nudge
        score += 0.10 * (opp_access - dist(ox, oy, tx, ty))     # usually 0, but keeps tie-break stable
        score -= 3.0 if hit else 0.0
        score += -0.03 * opp_d  # also drift away from being pulled off our line
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move