def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        best_target = None
        best_gain = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            gain = (do - ds) * 1000 - ds  # prefer resources we can reach earlier
            if gain > best_gain:
                best_gain = gain
                best_target = (rx, ry)
        rx, ry = best_target
        best_move = [0, 0]
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            ds_next = cheb(nx, ny, rx, ry)
            do_next = cheb(nx, ny, ox, oy)
            # progress to target; then prefer staying away from opponent slightly
            score = -ds_next * 10 - do_next
            # deterministic tie-break: prefer moves with smaller (dx,dy) lex order
            if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
                best_score = score
                best_move = [dx, dy]
        return best_move
    else:
        # No visible resources: drift toward center while staying away from opponent
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_move = [0, 0]
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dist_center = cheb(nx, ny, cx, cy)
            dist_opp = cheb(nx, ny, ox, oy)
            score = -dist_center * 10 + dist_opp
            if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
                best_score = score
                best_move = [dx, dy]
        return best_move