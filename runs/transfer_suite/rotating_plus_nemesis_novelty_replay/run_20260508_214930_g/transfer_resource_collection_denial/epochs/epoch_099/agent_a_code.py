def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    my_half_right = (sx <= w // 2)
    opp_half_right = (ox <= w // 2)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            nx, ny = sx, sy

        pos = (nx, ny)
        step_bonus = 0
        for (rx, ry) in resources:
            if rx == nx and ry == ny:
                step_bonus = 5000
                break

        # Choose the target resource that best creates advantage for us after this step.
        local_best = -10**18
        for (rx, ry) in resources:
            rpos = (rx, ry)
            md = cheb(pos, rpos)
            od = cheb((ox, oy), rpos)
            # Strongly prefer resources where we are not behind.
            base = 10000 - md * 40
            if md <= od:
                val = base + (od - md) * 120
            else:
                val = - (md - od) * 220 - md * 5
            # Mild preference to keep pushing toward the more "available" half.
            if (rx <= w // 2) == my_half_right:
                val += 15
            if (rx <= w // 2) == opp_half_right:
                val -= 10
            if val > local_best:
                local_best = val

        score = local_best + step_bonus
        # Deterministic tie-break: closer to the best local target.
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if cheb((sx, sy), (sx + best_move[0], sy + best_move[1])) > cheb((sx, sy), pos):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]