def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def kingd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def move_score(nx, ny):
        if not resources:
            # Drift toward far corner while keeping distance from opponent (deny symmetry traps)
            tx, ty = w - 1, h - 1
            return kingd(nx, ny, ox, oy) * 10 - (abs(tx - nx) + abs(ty - ny)) * 0.1

        best_adv = -10**9
        min_selfd = 10**9
        win_count = 0
        tie_count = 0

        for rx, ry in resources:
            sd = kingd(nx, ny, rx, ry)
            od = kingd(ox, oy, rx, ry)
            adv = od - sd  # positive means we're closer than they are (useful against deniers)
            if adv > best_adv:
                best_adv = adv
            if sd < min_selfd:
                min_selfd = sd
            if adv > 0:
                win_count += 1
            elif adv == 0:
                tie_count += 1

        # Strong preference for having an immediate "closer-to-something" advantage,
        # then for reducing our distance to the best resource, and finally for denying by crowding ties.
        return win_count * 1000 + best_adv * 10 - min_selfd * 2 - tie_count * 3

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        v = move_score(nx, ny)
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]