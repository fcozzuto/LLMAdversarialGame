def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    dxs = (-1, 0, 1)
    candidates = []
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy))
    if not candidates:
        return [0, 0]

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    def best_target_for(posx, posy, oppx, oppy):
        if not resources:
            return None, -10**9
        best = None
        best_val = -10**9
        for rx, ry in resources:
            sd = cheb(posx, posy, rx, ry)
            od = cheb(oppx, oppy, rx, ry)
            v = (od - sd)  # positive if we are closer than opponent
            # slight preference for nearer overall and for picking non-identical targets deterministically
            v += -0.01 * sd + 0.001 * ((rx * 8 + ry) % 97)
            # if resource is currently at/near our candidate position, boost to avoid dithering
            if sd == 0:
                v += 5
            best if best is not None else None
            if v > best_val:
                best_val = v
                best = (rx, ry)
        return best, best_val

    # Evaluate each candidate by advantage over opponent on the best shared target, plus safety
    best_move = (0, 0)
    best_score = -10**18
    target, _ = best_target_for(sx, sy, ox, oy)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        _, base = best_target_for(nx, ny, ox, oy)
        # safety: discourage stepping adjacent to opponent unless it also improves target advantage
        adj = cheb(nx, ny, ox, oy)
        safety = -0.6 if adj <= 1 else 0.0
        # small tie-break toward moving generally toward opponent's likely chase direction
        toward_opp = -0.01 * cheb(nx, ny, target[0], target[1]) if target else 0.0
        score = base + safety + toward_opp
        # deterministic tie-break: prefer smaller manhattan displacement then lexical (dx,dy)
        man = abs(dx) + abs(dy)
        score2 = score * 1000 - man
        if score2 > best_score:
            best_score = score2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]