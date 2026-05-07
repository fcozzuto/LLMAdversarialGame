def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Race heuristic: prefer resources we can arrive earlier; otherwise maximize time advantage.
    best = None
    best_score = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Small bias to reduce "mirror sweep": prefer resources nearer to our corner parity.
        parity_bias = 0.02 * (1 if ((rx + ry) & 1) == ((sx + sy) & 1) else -1)
        # If tie in arrival time, prefer the one with closer actual distance to us (more likely to secure).
        tie_bias = -0.001 * ds
        score = (do - ds) * 10.0 + parity_bias + tie_bias
        if do >= ds:
            score += 50.0  # strong commitment when we can "own" by arriving no later
        if score > best_score:
            best_score = score
            best = (rx, ry)

    rx, ry = best
    # Choose a safe move that reduces distance to target.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_d = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, rx, ry)
        # Tie-break: avoid stepping too close to opponent when we're losing the race.
        lose = 1 if cheb(sx, sy, rx, ry) > cheb(ox, oy, rx, ry) else 0
        opp_close = cheb(nx, ny, ox, oy)
        score = d + (0.001 * opp_close if lose else 0.0) + (0.0005 * (1 if (dx, dy) == (0, 0) else 0))
        if score < best_d:
            best_d = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]