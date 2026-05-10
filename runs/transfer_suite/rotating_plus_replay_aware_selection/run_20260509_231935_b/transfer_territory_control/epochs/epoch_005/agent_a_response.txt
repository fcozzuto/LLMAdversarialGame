def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obs = observation.get("obstacles", []) or []
    obs_set = {tuple(p) for p in obs}

    self_terr = observation.get("self_territory", []) or []
    opp_terr = observation.get("opponent_territory", []) or []
    unclaimed = observation.get("unclaimed_cells", []) or []

    self_set = {tuple(p) for p in self_terr}
    opp_set = {tuple(p) for p in opp_terr}
    un_set = {tuple(p) for p in unclaimed}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def min_dist_to(points, x, y):
        best = 10**9
        for px, py in points:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    # If we can, grab adjacent opponent territory; otherwise expand toward unclaimed near opponent.
    opp_list = list(opp_set)
    un_list = list(un_set)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    # Precompute opponent "hotness": count how many adjacent opponent tiles each cell has (cheap via local checks).
    def opp_adjacent(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in opp_set:
                    c += 1
        return c

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        val = 0
        if (nx, ny) in opp_set:
            val += 500  # direct flip
        elif (nx, ny) in un_set:
            val += 120  # claim unclaimed
        elif (nx, ny) in self_set:
            val += 10   # keep territory

        # Prefer moving toward good targets, but still reward proximity to opponent for contested areas.
        if un_list:
            d_un = min_dist_to(un_list, nx, ny)
            val += 30 / (1 + d_un)
        if opp_list:
            d_opp = min_dist_to(opp_list, nx, ny)
            val += 20 / (1 + d_opp)

        # Increase value near opponent boundary to counter sweeper.
        val += 25 * opp_adjacent(nx, ny)

        # Slightly avoid getting stuck: keep improving distance to some unclaimed if possible.
        if un_list:
            d_now = min_dist_to(un_list, sx, sy)
            if abs(d_now - (min_dist_to(un_list, nx, ny))) <= 0:
                val -= 2

        # Deterministic tie-break: lexicographically smallest move among equals.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]