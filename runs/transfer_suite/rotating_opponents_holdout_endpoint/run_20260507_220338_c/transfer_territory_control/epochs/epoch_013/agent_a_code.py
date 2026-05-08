def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    my_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    my_set = set((int(x), int(y)) for x, y in my_terr if inside(int(x), int(y)))
    opp_set = set((int(x), int(y)) for x, y in opp_terr if inside(int(x), int(y)))
    un_set = set((int(x), int(y)) for x, y in unclaimed if inside(int(x), int(y)))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    def neigh_in_set(x, y, s):
        for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) in s:
                return True
        return False

    opp_pos = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        if (nx, ny) in my_set:
            cell_score = -2
        elif (nx, ny) in opp_set:
            cell_score = 8
        elif (nx, ny) in un_set:
            cell_score = 6
        else:
            cell_score = 1

        # Prefer grabbing territory near opponent and reducing distance to opponent
        adj_opp = 1 if neigh_in_set(nx, ny, opp_set) else 0
        dist = abs(nx - ox) + abs(ny - oy)
        proximity = -dist * 0.15

        # Encourage leaving current territory edge toward unclaimed/opp
        adj_me = 1 if neigh_in_set(nx, ny, my_set) else 0
        edge_bias = (2 if adj_opp else 0) + (1 if adj_me == 0 else 0)

        score = cell_score + 3.5 * adj_opp + proximity + edge_bias
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move