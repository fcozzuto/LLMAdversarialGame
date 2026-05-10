def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                m += 1
        return m

    # Predict opponent step toward our current position (turn-start), ignoring their obstacles (robust enough).
    def predicted_opponent_position():
        best = None
        bestd = 10**9
        for dx, dy in deltas:
            nx, ny = ox + dx, oy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            d = cheb(nx, ny, sx, sy)
            if d < bestd:
                bestd = d
                best = (nx, ny, dx, dy)
        return (best[0], best[1]) if best else (ox, oy)

    pax, pay = predicted_opponent_position()

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_opp = cheb(nx, ny, ox, oy)
        d_from_pred = cheb(nx, ny, pax, pay)
        # Strongly prefer reducing distance to opponent; secondarily keep away from predicted pursuit; finally keep options.
        score = (-10 * d_to_opp) + (2 * d_from_pred) + (0.7 * mobility(nx, ny))
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]