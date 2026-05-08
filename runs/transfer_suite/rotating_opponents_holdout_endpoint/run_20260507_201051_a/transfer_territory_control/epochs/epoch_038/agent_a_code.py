def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_to_self(x, y):
        for ax, ay in neigh:
            if (x + ax, y + ay) in self_t:
                return True
        return False

    def adj_count_to_self(x, y):
        c = 0
        for ax, ay in neigh:
            if (x + ax, y + ay) in self_t:
                c += 1
        return c

    def adj_count_to_opp(x, y):
        c = 0
        for ax, ay in neigh:
            if (x + ax, y + ay) in opp_t:
                c += 1
        return c

    best_sc = -10**18
    best_move = (0, 0)

    # Frontier targets: unclaimed cells adjacent to us
    frontier = []
    for ux, uy in unclaimed:
        if adj_to_self(ux, uy):
            d = abs(ux - sx) + abs(uy - sy)
            # Prefer cells that are not "too open" (keep pressure near front)
            frontier.append((d, -adj_count_to_self(ux, uy), -adj_count_to_opp(ux, uy), ux, uy))
    frontier.sort()

    # Also consider direct captures adjacent to opponent territory
    capture_candidates = []
    for ax, ay in [(sx + dx, sy + dy) for dx, dy in neigh + [(0, 0)]]:
        if valid(ax, ay) and (ax, ay) in opp_t:
            capture_candidates.append((0, -adj_count_to_self(ax, ay), -adj_count_to_opp(ax, ay), ax, ay))
    if capture_candidates:
        # ensure deterministic: evaluate capture moves via normal loop below
        pass

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        sc = 0
        if (nx, ny) in opp_t:
            sc += 5000
        if (nx, ny) in unclaimed:
            sc += 40
        if (nx, ny) in self_t:
            sc += 3

        # Maintain/extend our connected front
        sc += 25 * adj_count_to_self(nx, ny)

        # Pressure near opponent (even if not capturing)
        sc += 10 * adj_count_to_opp(nx, ny)

        # Move toward nearest frontier cell if possible
        if frontier:
            d0, a0, b0, tx, ty = frontier[0]
            sc += -2.0 * (abs(nx - tx) + abs(ny - ty))
            # If we are not adjacent to our territory, don't stray too far
            if adj_to_self(nx, ny):
                sc += 15
            else:
                sc -= 8

        # Slightly discourage staying if a legal frontier step exists
        if dx == 0 and dy == 0 and frontier:
            sc -= 6

        if sc > best_sc or (sc == best_sc and (dx, dy) < best_move):
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]