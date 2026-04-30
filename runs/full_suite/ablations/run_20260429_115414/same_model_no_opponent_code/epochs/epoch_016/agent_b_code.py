def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}

    resources = observation.get("resources") or []
    res = [(int(p[0]), int(p[1])) for p in resources]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def move_ok(dx, dy):
        nx, ny = sx + dx, sy + dy
        return inb(nx, ny) and (nx, ny) not in obs

    best_move = (0, 0)
    best_score = None

    if res:
        # Reaching race: prioritize resources where opponent is farther than us (big), then nearer to us.
        for dx, dy in moves:
            if not move_ok(dx, dy):
                continue
            nx, ny = sx + dx, sy + dy
            sd0 = cheb(nx, ny, ox, oy)
            s_base = 0
            # slight penalty if we move closer to opponent (gives them easier contest)
            # (keeping deterministic, no extra search)
            score = -sd0
            for rx, ry in res:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # if opponent can arrive no later, strongly discourage
                margin = od - sd
                v = margin * 120 - sd * 3
                # encourage resources generally in our "half" (based on start corner diagonal)
                if sx >= w // 2:
                    # for typical agent_b in bottom-right, favor larger x and y
                    v += (rx + ry) // 2
                else:
                    v += ((w - 1 - rx) + (h - 1 - ry)) // 2
                if v > s_base:
                    s_base = v
            total = score + s_base
            if best_score is None or total > best_score or (total == best_score and (dx, dy) < best_move):
                best_score = total
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources visible: deterministically move toward center while avoiding obstacles.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_d = None
    for dx, dy in moves:
        if not move_ok(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        d = abs(nx - cx) + abs(ny - cy)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_move):
            best_d = d
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]