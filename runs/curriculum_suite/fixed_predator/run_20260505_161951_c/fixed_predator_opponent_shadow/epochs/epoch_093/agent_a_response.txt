def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If no resources, drift toward midpoint between agents.
    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            key = (md(nx, ny, tx, ty), md(nx, ny, ox, oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    best = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # Choose a target resource that balances: closeness for us, slowness for opponent.
        # Evaluate best achievable "advantage" at the next step (maximizing).
        best_adv = None
        best_res_tiebreak = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Prefer immediate reach advantage; if equal, prefer reducing our distance.
            adv = (od - sd, -sd)
            tieb = (rx, ry)
            if best_adv is None or adv > best_adv or (adv == best_adv and tieb < best_res_tiebreak):
                best_adv = adv
                best_res_tiebreak = tieb
        # Global move key: maximize advantage; then minimize our distance to nearest resource;
        # and finally keep movement stable and away from opponent if tied.
        nearest_sd = min(md(nx, ny, rx, ry) for rx, ry in resources)
        dist_to_opp = md(nx, ny, ox, oy)
        key = (-(best_adv[0]), nearest_sd, -dist_to_opp, dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))

    return [best[1][0], best[1][1]]