def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    blocked = {(p[0], p[1]) for p in obstacles}

    def obstacle_penalty(x, y):
        pen = 0
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d == 0:
                pen += 1000
            elif d == 1:
                pen += 25
            elif d == 2:
                pen += 6
        return pen

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in blocked:
            continue

        # Prefer moves that improve our "race" to a resource where we can arrive earlier.
        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in blocked:
                continue
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Higher means we are closer (or opponent is farther).
            advantage = opp_d - self_d
            # Small tie-break: prefer resources closer to us (lower self_d).
            score = advantage * 10 - self_d
            if score > local_best:
                local_best = score

        total = local_best - obstacle_penalty(nx, ny)
        # Deterministic tie-break: lexicographic by delta order due to fixed deltas.
        if total > best_score:
            best_score = total
            best_move = [dx, dy]

    return best_move