def choose_move(observation):
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Choose a target resource: prioritize where we are closer than opponent.
    best_t = None
    best_adv = -10**9
    for rx, ry in resources:
        d1 = abs(rx - x) + abs(ry - y)
        d2 = abs(rx - ox) + abs(ry - oy)
        adv = d2 - d1
        if adv > best_adv or (adv == best_adv and (best_t is None or d1 < (abs(best_t[0]-x)+abs(best_t[1]-y)))):
            best_adv = adv
            best_t = (rx, ry)
    if best_t is None:
        best_t = (ox, oy)  # fallback deterministic

    tx, ty = best_t

    def valid(nx, ny):
        if nx < 0 or ny < 0 or nx >= gw or ny >= gh:
            return False
        if (nx, ny) in obstacles:
            return False
        return True

    # If opponent is clearly closer to the target, try to block by moving to a cell that reduces their advantage.
    opp_closer = (abs(tx - ox) + abs(ty - oy)) <= (abs(tx - x) + abs(ty - y))

    cur_dist = abs(tx - x) + abs(ty - y)
    cur_sep = abs(ox - x) + abs(oy - y)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        ndist = abs(tx - nx) + abs(ty - ny)
        nsep = abs(ox - nx) + abs(oy - ny)
        # Base: go to target (prefer strict improvement)
        score = -ndist * 3 + (cur_dist - ndist) * 10
        # Avoid getting too close to opponent (prevents easy capture after reaching resources)
        score += nsep * 0.5
        # If opponent is closer, prioritize moves that increase their path length to target (proxy via distance)
        if opp_closer:
            odist_next = abs(tx - ox) + abs(ty - oy)
            # proxy: maximize our distance reduction while keeping opponent farther from target is not possible directly,
            # so instead increase separation and avoid enabling them by not moving adjacent to them.
            score += (nsep - cur_sep) * 6
            if max(abs(ox - nx), abs(oy - ny)) <= 1 and nsep < cur_sep:
                score -= 25
        # Slight deterministic tie-break: prefer not to stay still unless it's best
        if dx == 0 and dy == 0:
            score -= 0.1
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]