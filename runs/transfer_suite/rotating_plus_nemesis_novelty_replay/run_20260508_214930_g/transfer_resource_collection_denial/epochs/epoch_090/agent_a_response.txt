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
    seen = set()
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) not in seen:
                seen.add((x, y))
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick a target resource that we are likely to reach first, with tie-break toward being closer and advancing away from opponent.
    # Use only current positions (deterministic, cheap).
    best_target = resources[0]
    best_score = -10**18
    for t in resources:
        ds = cheb((sx, sy), t)
        do = cheb((ox, oy), t)
        if do == ds:
            pr = 0
        else:
            pr = (do - ds)  # positive if we are closer
        # slight preference for resources nearer to bottom-right diagonal progression (reduces dithering on empty fronts)
        diag = abs((t[0] + t[1]) - (w + h - 2) * 0.5)
        score = pr * 10 - ds * 2 - diag * 0.1
        if score > best_score:
            best_score = score
            best_target = t

    tx, ty = best_target

    # One-step lookahead: choose move maximizing improvement in our distance to target, but avoid stepping onto obstacles/out of bounds.
    # If multiple moves tie, prefer moves that also increase distance from opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        ns = cheb((nx, ny), (tx, ty))
        cur = cheb((sx, sy), (tx, ty))
        do_next = cheb((ox, oy), (tx, ty))
        # improvement component
        improve = cur - ns
        # prevent chasing a target the opponent is closer to by maximizing (ds - do) after the move
        ds_next = ns
        margin = do_next - ds_next  # positive is good for us
        opp_dist = cheb((nx, ny), (ox, oy))
        val = improve * 5 + margin * 3 + opp_dist * 0.05
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]