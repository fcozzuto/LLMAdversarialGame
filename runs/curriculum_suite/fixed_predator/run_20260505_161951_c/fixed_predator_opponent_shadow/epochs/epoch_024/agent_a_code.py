def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        # When no resources, move to maximize distance from opponent (reduce contest pressure)
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in moves:
            v = abs(nx - ox) + abs(ny - oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # New strategy: evaluate each move by the best achievable "advantage" on any resource
    # Advantage = (opponent distance) - (self distance); prefer moves that increase it.
    # Tie-break: prefer closer to a resource, and also slightly steer away from opponent.
    best = (0, 0)
    best_score = -10**18
    for dx, dy, nx, ny in moves:
        best_adv = -10**18
        best_selfd = 10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and sd < best_selfd):
                best_adv = adv
                best_selfd = sd
        # Encourage breaking ties by improving our situation vs opponent and keeping space
        score = (best_adv * 1000) - best_selfd - 0.1 * (man(nx, ny, ox, oy))
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]