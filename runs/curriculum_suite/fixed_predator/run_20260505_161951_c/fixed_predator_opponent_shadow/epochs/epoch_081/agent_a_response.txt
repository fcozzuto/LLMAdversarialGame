def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - tx) + abs(ny - ty)
            key = (d, abs(nx - ox) + abs(ny - oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    best_key = None
    best_move = (0, 0)
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        best_pot = None
        best_self_d = None
        best_opp_d = None
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            pot = od - sd  # positive means we are closer than opponent for this resource
            if best_pot is None or pot > best_pot or (pot == best_pot and sd < best_self_d):
                best_pot, best_self_d, best_opp_d = pot, sd, od

        # Prefer moves that create advantage; otherwise, still head to nearest resource,
        # and reduce opponent proximity only as a secondary tie-break.
        score_adv = best_pot
        self_term = best_self_d
        opp_term = best_opp_d

        key = (
            -(score_adv * 1000 + (200 - min(self_term, 200))),  # maximize advantage strongly, then self distance
            self_term,  # then reduce distance
            abs(nx - ox) + abs(ny - oy),  # then avoid getting too close to opponent (deterministic)
            dx, dy
        )
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]