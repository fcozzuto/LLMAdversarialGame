def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_val = -10**18

    # Precompute to keep evaluation deterministic and small
    unclaimed_list = unclaimed
    n_un = len(unclaimed_list)
    opp_list = list(opp_terr)
    s_list = list(self_terr)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0
        cell = (nx, ny)

        if cell in unclaimed:
            val += 450
        if cell in self_terr:
            val += 18
        if cell in opp_terr:
            val += 120  # flipping on entry is enabled

        # Gain toward nearest unclaimed from the candidate cell
        if n_un:
            d_self = 10**9
            d_opp = 10**9
            for (ux, uy) in unclaimed_list:
                d = abs(ux - nx) + abs(uy - ny)
                if d < d_self:
                    d_self = d
                do = abs(ux - px) + abs(uy - py)
                if do < d_opp:
                    d_opp = do
            # Prefer cells that are closer to unclaimed than opponent is
            val += 70 * (d_opp - d_self)
            val += 35 * (-d_self)

        # Slight preference to approach/contest opponent territory boundary
        if opp_list:
            d_to_opp = 10**9
            do_to_opp = 10**9
            for (ox, oy) in opp_list:
                d = abs(ox - nx) + abs(oy - ny)
                if d < d_to_opp:
                    d_to_opp = d
                d2 = abs(ox - px) + abs(oy - py)
                if d2 < do_to_opp:
                    do_to_opp = d2
            val += 20 * (do_to_opp - d_to_opp)
            val += -8 * d_to_opp

        # Avoid stepping away from our territory when no unclaimed advantage exists
        if not n_un and s_list:
            d_back = 10**9
            for (tx, ty) in s_list:
                d = abs(tx - nx) + abs(ty - ny)
                if d < d_back:
                    d_back = d
            val += -6 * d_back

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best