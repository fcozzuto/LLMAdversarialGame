def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    # Precompute distance to closest opponent territory cell
    opp_list = list(opp_t)
    if not opp_list:
        opp_list = [(ox, oy)]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        # Base: expand into unclaimed; take opponent territory if possible
        val = 0
        if cell in self_t:
            val += 6
        if cell in unclaimed:
            val += 120
        if cell in opp_t:
            val += 35  # flipping likely changes control

        # Encourage approaching farthest useful unclaimed while maintaining defense
        # (use nearest target heuristic)
        # Score closeness to unclaimed targets and closeness to opponent territory
        if unclaimed:
            # prefer reducing distance to nearest unclaimed
            d_target = min(abs(nx - tx) + abs(ny - ty) for tx, ty in unclaimed)
            val += max(0, 60 - d_target)
        d_opp = min(abs(nx - tx) + abs(ny - ty) for tx, ty in opp_list)
        val += max(0, 18 - d_opp)  # being near opponent territory can help flip it

        # Defensive: avoid stepping away from own mass if already strong
        if observation.get("self_territory_count", 0) >= observation.get("opponent_territory_count", 0):
            d_self = min(abs(nx - tx) + abs(ny - ty) for tx, ty in self_t) if self_t else abs(nx - sx) + abs(ny - sy)
            val += max(0, 10 - d_self)

        # Extra tie-breaker: prefer reducing distance to opponent position when threatening
        val += -0.5 * (abs(nx - ox) + abs(ny - oy))

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]