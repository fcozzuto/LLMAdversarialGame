def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not inb(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    if resources:
        best_r = None
        best_val = -10**18
        best_us_d = 10**9
        for rx, ry in resources:
            ds = dist_cheb(sx, sy, rx, ry)
            do = dist_cheb(ox, oy, rx, ry)
            val = do - ds  # prefer resources where we are closer than opponent
            if val > best_val or (val == best_val and ds < best_us_d):
                best_val = val
                best_us_d = ds
                best_r = (rx, ry)

        rx, ry = best_r
        best_move = (0, 0)
        best_score = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            ds_next = dist_cheb(nx, ny, rx, ry)
            do = dist_cheb(ox, oy, rx, ry)
            contest = do - ds_next
            tie_break = -ds_next
            # slight bias: move away from obstacles adjacency isn't needed; just prefer improving contest
            score = contest * 1000 + tie_break
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move to deny opponent by heading toward them
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d1 = dist_cheb(nx, ny, ox, oy)
        score = -d1  # minimize distance to opponent
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]