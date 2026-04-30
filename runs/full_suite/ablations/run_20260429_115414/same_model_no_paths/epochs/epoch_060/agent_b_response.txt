def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18
    opp_best_d = None
    if resources:
        opp_best_d = min(cheb(ox, oy, rx, ry) for rx, ry in resources)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            max_adv = -10**9
            min_our_d_for_best = 10**9
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                adv = do - ds  # positive means we are closer than opponent to this resource
                if adv > max_adv or (adv == max_adv and ds < min_our_d_for_best):
                    max_adv = adv
                    min_our_d_for_best = ds

            # Primary: maximize advantage (we-there-first)
            # Secondary: also prefer reducing opponent's overall closest-resource distance
            opp_min_d = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
            score = max_adv * 1000 - min_our_d_for_best * 3 + (opp_best_d - opp_min_d) * 2
            # Small deterministic tie-break: prefer staying on even parity
            if (nx + ny) % 2 == 0:
                score += 1
        else:
            # No resources: move to reduce distance to opponent to contest center of future gains
            score = -cheb(nx, ny, ox, oy)
            if (nx + ny) % 2 == 0:
                score += 1

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]