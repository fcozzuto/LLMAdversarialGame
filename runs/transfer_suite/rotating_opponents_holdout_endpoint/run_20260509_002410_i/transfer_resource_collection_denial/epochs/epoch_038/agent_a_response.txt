def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    # With diagonal moves allowed, minimal steps is Chebyshev distance.
    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose the move that maximizes "capture advantage":
    # advantage = (opponent_steps_to_r) - (my_steps_after_move_to_r)
    best_move = (0, 0)
    best = None
    tr = int(observation.get("turns_remaining", 0))
    urgency = 1.0 + (1.0 / (1.0 + tr))  # slightly prefer earlier
    my_dist_bias = 1.0 / urgency

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Compute best achievable advantage over all resources with this next position.
        best_adv = None
        best_my_d = None
        best_rx, best_ry = None, None
        for rx, ry in resources:
            my_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            adv = (opp_d - my_d) * urgency
            if best_adv is None or adv > best_adv or (adv == best_adv and (my_d < best_my_d or (my_d == best_my_d and (rx < best_rx or (rx == best_rx and ry < best_ry))))):
                best_adv = adv
                best_my_d = my_d
                best_rx, best_ry = rx, ry

        # Also break ties by preferring quicker pickup and then lexicographic move.
        key = (best_adv, -best_my_d * my_dist_bias, -dx, -dy)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]