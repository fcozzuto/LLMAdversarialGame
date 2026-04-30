def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer moves that get closer to a resource where we are also closer than opponent.
    # If no resources, drift toward center while avoiding opponent.
    if resources:
        best_dx, best_dy = legal[0][0], legal[0][1]
        best_score = -10**18
        for dx, dy, nx, ny in legal:
            my_pos = (nx, ny)
            opp_pos = (ox, oy)
            score = 0
            # small preference for staying away from opponent to reduce contested pickups
            score -= 0.05 * man(my_pos, opp_pos)
            # evaluate best target resource for this move
            local_best = -10**18
            for rx, ry in resources:
                res = (rx, ry)
                d_my = man(my_pos, res)
                d_opp = man(opp_pos, res)
                # If we are closer, big positive; if opponent closer, negative.
                # Prefer smaller my distance when tie/near.
                v = (d_opp - d_my) * 5.0 - d_my * 0.3
                # Encourage moving toward resources that are "not behind" obstacles (light proxy: favor
                # resources with at least one clear step closer in x or y)
                step1 = (nx, ny)
                if step1[0] != sx or step1[1] != sy:
                    v += 0.1
                if v > local_best:
                    local_best = v
            score += local_best
            if score > best_score or (score == best_score and (dx, dy) < (best_dx, best_dy)):
                best_score = score
                best_dx, best_dy = dx, dy
        return [int(best_dx), int(best_dy)]
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_dx, best_dy = legal[0][0], legal[0][1]
        best_score = -10**18
        for dx, dy, nx, ny in legal:
            d_center = man((nx, ny), (cx, cy))
            d_opp = man((nx, ny), (ox, oy))
            score = -d_center + 0.02 * d_opp
            if score > best_score or (score == best_score and (dx, dy) < (best_dx, best_dy)):
                best_score = score
                best_dx, best_dy = dx, dy
        return [int(best_dx), int(best_dy)]