def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
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

    best_move = [0, 0]
    best_val = -10**9

    if resources:
        # For each move, prefer positions where we can reach some resource sooner than opponent.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles: 
                continue

            our_dist = []
            opp_dist = []
            for rx, ry in resources:
                our_dist.append(cheb(nx, ny, rx, ry))
                opp_dist.append(cheb(ox, oy, rx, ry))
            # Greedy: maximize best advantage; tie-break on closeness to best target.
            best_adv = -10**9
            best_our = 10**9
            for i in range(len(resources)):
                adv = opp_dist[i] - our_dist[i]
                if adv > best_adv or (adv == best_adv and our_dist[i] < best_our):
                    best_adv = adv
                    best_our = our_dist[i]

            # Slightly repel opponent to avoid being funneled.
            opp_prox = cheb(nx, ny, ox, oy)
            val = best_adv * 100 - best_our - (0 if dx == 0 and dy == 0 else 0) + opp_prox // 2
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        # No visible resources: move toward center while keeping distance from opponent.
        cx, cy = w // 2, h // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles: 
                continue
            val = -cheb(nx, ny, cx, cy) * 2 + cheb(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]