def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set()
    for p in observation.get("obstacles", []):
        obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Move preference order (deterministic): straight/diagonal toward advantage, then closer to resources.
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    # Choose the best move by maximizing (our advantage) with a stable tie-break.
    best_key = None
    best_move = [0, 0]

    # Also lightly bias to resources closer to our side of the board to beat row sweeps.
    side_bias = (w - 1 - sx) - sx  # positive when we are on right half, negative when on left half

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate resources reachable from the candidate position.
        best_adv = None
        best_our_d = None
        best_rx, best_ry = None, None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)

            # Advantage: we want to be closer than opponent; strongly prioritize immediate pickup.
            pickup = -1000 if our_d == 0 else 0
            # Tie-break to reduce race losses: smaller our_d after accounting for opponent distance.
            adv = (opp_d - our_d) + pickup

            # Bias toward resources on the same "direction" as our side (helps against sweep-rows).
            # Deterministic and mild: scale by (1 + our_d) to not override primary race logic.
            bias = -0.1 * (rx - (w / 2.0)) * (1 if side_bias <= 0 else -1)
            adv = adv - bias / (1 + our_d)

            if best_adv is None or adv > best_adv or (adv == best_adv and (best_our_d is None or our_d < best_our_d)):
                best_adv = adv
                best_our_d = our_d
                best_rx, best_ry = rx, ry

        if best_adv is None:
            continue

        # Choose action that maximizes advantage; tie-break by our distance, then by a stable coordinate order.
        key = (best_adv, -best_our_d if best_our_d is not None else 0, -(best_rx if best_rx is not None else 0), -(best_ry if best_ry is not None else 0), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move