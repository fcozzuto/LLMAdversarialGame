def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obs_list = observation.get("obstacles", [])
    obstacles = {(p[0], p[1]) for p in obs_list} if obs_list else set()

    self_cells = observation.get("self_territory", [])
    opp_cells = observation.get("opponent_territory", [])
    myc = observation.get("self_territory_count", len(self_cells)) if self_cells or "self_territory_count" in observation else 0
    opc = observation.get("opponent_territory_count", len(opp_cells)) if opp_cells or "opponent_territory_count" in observation else 0

    resources = observation.get("resources", [])
    resources = resources if isinstance(resources, list) else []

    # aggressive if behind
    aggressive = myc < opc
    tx, ty = (ox, oy)

    if not aggressive and resources:
        best = None
        bestd = 10**18
        for r in resources:
            rx, ry = r[0], r[1]
            d = abs(rx - sx) + abs(ry - sy)
            if d < bestd:
                bestd = d
                best = (rx, ry)
        if best is not None:
            tx, ty = best

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_to_target = abs(nx - tx) + abs(ny - ty)
        d_to_opp = abs(nx - ox) + abs(ny - oy)

        score = -d_to_target
        if aggressive:
            score += -0.1 * d_to_opp
        else:
            score += 0.05 * d_to_opp

        # small preference for staying near own territory
        if self_cells:
            score += 0.02 * (-min(abs(nx - x) + abs(ny - y) for (x, y) in self_cells))

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]