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

    dirs = [(-1, -1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    best = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if resources:
            my_best = 10**9
            opp_best = 10**9
            for rx, ry in resources:
                d_my = cheb(nx, ny, rx, ry)
                if d_my < my_best: my_best = d_my
                d_opp = cheb(ox, oy, rx, ry)
                if d_opp < opp_best: opp_best = d_opp
        else:
            my_best = 0
            opp_best = 0

        # Prefer moves that reduce my distance more than the opponent's (or increase it)
        score = (opp_best - my_best)

        # If I land on a resource, strongly commit
        if (nx, ny) in resources:
            score += 10000

        # Small preference to move away from opponent when resources are scarce
        if not resources:
            score += cheb(nx, ny, ox, oy) * 0.01

        key = (-(score), dx, dy)  # deterministic tie-break
        if best_val is None or key < best_val:
            best_val = key
            best = (dx, dy)

    return [best[0], best[1]]