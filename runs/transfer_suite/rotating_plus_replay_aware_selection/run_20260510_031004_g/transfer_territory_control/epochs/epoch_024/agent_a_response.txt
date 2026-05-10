def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a deterministic target: nearest unclaimed, tie by x then y
    if unclaimed:
        ux, uy = min(unclaimed, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
        tx, ty = ux - sx, uy - sy
        step_x = 0 if tx == 0 else (1 if tx > 0 else -1)
        step_y = 0 if ty == 0 else (1 if ty > 0 else -1)
    else:
        step_x = step_y = 0

    s_count = int(observation.get("self_territory_count", len(self_terr)))
    o_count = int(observation.get("opponent_territory_count", len(opp_terr)))
    we_are_behind = 1 if s_count < o_count else 0

    best = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0

        if (nx, ny) in unclaimed:
            val += 420 + 20 * we_are_behind
        elif (nx, ny) in opp_terr:
            val += 280 + 40 * we_are_behind  # flipping on entry
        elif (nx, ny) in self_terr:
            val += 35

        # Prefer moves that advance toward the chosen unclaimed target
        if (dx, dy) == (step_x, step_y) or (dx == step_x and (dy == 0 or step_y == 0)):
            val += 60
        # Small shaping toward target even if diagonal isn't exact
        val += -2 * (abs(nx - (sx + tx)) + abs(ny - (sy + ty))) if unclaimed else 0

        # If opponent is adjacent, prioritize contesting (entering opp territory or unclaimed)
        if max(abs(nx - px), abs(ny - py)) == 1:
            if (nx, ny) in opp_terr:
                val += 120
            if (nx, ny) in unclaimed:
                val += 80

        # Avoid drifting away when unclaimed exists
        if unclaimed:
            cur_d = abs(sx - ux) + abs(sy - uy)
            nxt_d = abs(nx - ux) + abs(ny - uy)
            val += (cur_d - nxt_d) * 12

        # Deterministic tie-break: choose lexicographically smallest move among equals
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]