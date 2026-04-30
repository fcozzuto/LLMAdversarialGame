def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    try:
        rem = int(observation.get("remaining_resource_count") or 0)
    except:
        rem = 0
    late = rem <= 4

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def blocked_risk(nx, ny):
        # Penalize cells with many neighboring obstacles (deterministic local avoidance)
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                x, y = nx + dx, ny + dy
                if not (0 <= x < w and 0 <= y < h):
                    cnt += 1
                elif (x, y) in obstacles:
                    cnt += 1
        return cnt

    def best_score(cx, cy):
        if not resources:
            # Move to center to reduce opponent leverage
            tx, ty = w // 2, h // 2
            return -cheb(cx, cy, tx, ty)

        # Prefer resources where we can arrive earlier than opponent; late-game tighten race
        best = -10**18
        for rx, ry in resources:
            ds = cheb(cx, cy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If late, strongly bias winning the race; otherwise also prefer closeness to resources.
            if late:
                s = (do - ds) * 10 - ds - blocked_risk(cx, cy) * 0.3
            else:
                s = (do - ds) * 6 - ds * 1.5 - blocked_risk(cx, cy) * 0.2
            if s > best:
                best = s
        return best

    # Deterministic tie-breaking: prefer smaller (dx,dy) in listed order, and then prioritize moving towards best by score.
    best_move = (0, 0)
    best = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = best_score(nx, ny)
        if sc > best:
            best = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]