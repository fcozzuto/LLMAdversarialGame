def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) == 2:
            obstacles.add((p[0], p[1]))
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = (10**18, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny): 
                continue
            d = cheb(nx, ny, ox, oy)
            # Prefer moves that reduce distance to opponent, then keep within safe-ish direction
            key = (d, abs(nx-ox) + abs(ny-oy), dx*10+dy)
            if key < best:
                best = key
        return [best[2]//10, best[2]%10]

    # Deterministic tie-break: iterate resources in fixed order
    resources_sorted = sorted([(r[0], r[1]) for r in resources])
    best_move = (10**18, 0, 0, 0)  # key, dx, dy
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Evaluate best target for this move; aim to be closer than opponent, else deny
        best_key_for_move = (10**18, 10**18, 0, 0)
        for rx, ry in resources_sorted:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # If we are closer, prioritize absolute proximity and being closer than opponent
            # If not, prioritize making (myd - opd) as small as possible (deny)
            rel = myd - opd
            # Also slight preference for moving toward opponent overall to break ties
            key = (0 if rel <= 0 else 1, abs(rel), myd, cheb(nx, ny, ox, oy))
            if key < best_key_for_move:
                best_key_for_move = key
        # Final deterministic key: prefer best target evaluation; then prefer smaller cheb to opponent
        final_key = (best_key_for_move[0], best_key_for_move[1], best_key_for_move[2], best_key_for_move[3], dx, dy)
        if final_key < best_move:
            best_move = (final_key[0], dx, dy, final_key[1])
    return [best_move[1], best_move[2]]