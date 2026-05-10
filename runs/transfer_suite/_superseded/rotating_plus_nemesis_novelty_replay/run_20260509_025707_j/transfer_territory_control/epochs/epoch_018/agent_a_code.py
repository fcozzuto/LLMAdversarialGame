def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    self_cells = set(tuple(p) for p in observation.get("self_territory", []) or [])
    opp_cells = set(tuple(p) for p in observation.get("opponent_territory", []) or [])
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells", []) or [])

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh_opp_adj(x, y):
        c = 0
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) in opp_cells:
                c += 1
        return c

    def dist_to_op(x, y):
        return abs(x - ox) + abs(y - oy)

    best_score = -10**18
    best_move = [0, 0]

    # Deterministic tie-break: fixed move ordering by index in neigh.
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in self_cells:
            score = 5.0 - 0.05 * dist_to_op(nx, ny)
        elif (nx, ny) in opp_cells:
            # Strongly reward flips; prefer closer to opponent.
            score = 120.0 - 0.8 * dist_to_op(nx, ny) - 0.2 * neigh_opp_adj(nx, ny)
        elif (nx, ny) in unclaimed:
            # Expand toward opponent and border cells.
            score = 55.0 + 6.0 * neigh_opp_adj(nx, ny) - 0.6 * dist_to_op(nx, ny)
        else:
            # Unknown/rare cell types: mild preference for moving toward opponent.
            score = 2.0 - 0.3 * dist_to_op(nx, ny) + 0.2 * neigh_opp_adj(nx, ny)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move