def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(x, y):
        if x < 0: x = 0
        if x >= w: x = w - 1
        if y < 0: y = 0
        if y >= h: y = h - 1
        return x, y

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, move toward opponent to contest space deterministically
    if not resources:
        best = [0, 0, -10**9]
        for dx, dy in dirs:
            nx, ny = clamp(sx + dx, sy + dy)
            if (nx, ny) in obstacles:
                continue
            score = -cheb(nx, ny, ox, oy)
            if score > best[2]:
                best = [dx, dy, score]
        return [best[0], best[1]]

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue

        # Choose a target resource where we have the biggest advantage
        best_adv = -10**18
        best_res_dist = 10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            adv = oppd - myd  # positive means I'm closer/tied
            if adv > best_adv or (adv == best_adv and myd < best_res_dist):
                best_adv = adv
                best_res_dist = myd

        # Small tie-break: prefer moving closer to opponent if advantages are equal (denser contest)
        tie = -cheb(nx, ny, ox, oy)
        score = best_adv * 1000 - best_res_dist + tie
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move