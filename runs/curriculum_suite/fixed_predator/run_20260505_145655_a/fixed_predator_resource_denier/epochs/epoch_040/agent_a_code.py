def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Target resource that opponent is closest to (for contesting/denial).
    best_opp = None
    best_oppd = 10**9
    for rx, ry in resources:
        d = abs(ox - rx) + abs(oy - ry)
        if d < best_oppd:
            best_oppd = d
            best_opp = (rx, ry)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        local_best = -10**18
        selfd_to_opp = abs(nx - ox) + abs(ny - oy)

        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            adv = oppd - selfd  # positive means we are closer after the move
            # Main objective: maximize advantage; second: finish sooner; third: avoid being too far behind.
            sc = adv * 10 - selfd
            if adv <= 0:
                sc = adv * 4 - selfd * 1.2
            # If this is the opponent's closest target, heavily contest it.
            if best_opp is not None and (rx, ry) == best_opp:
                sc += (3.5 if best_oppd <= 2 else 2.0) * (adv if adv > 0 else -2.0)
                sc += max(0, 6 - best_oppd) * (1 if selfd <= best_oppd else -0.5)
            # Soft preference: don't move into very low-quality zones (too far from best resources).
            sc -= 0.05 * selfd_to_opp
            if sc > local_best:
                local_best = sc

        if local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]