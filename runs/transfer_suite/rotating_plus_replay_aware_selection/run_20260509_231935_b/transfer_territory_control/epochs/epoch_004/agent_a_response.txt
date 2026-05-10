def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = observation.get("obstacles", [])
    obs_set = {tuple(p) for p in obstacles}

    self_terr = observation.get("self_territory", []) or []
    opp_terr = observation.get("opponent_territory", []) or []
    unclaimed = observation.get("unclaimed_cells", []) or []

    self_set = {tuple(p) for p in self_terr}
    opp_set = {tuple(p) for p in opp_terr}
    un_set = {tuple(p) for p in unclaimed}

    opp_list = list(opp_set)
    un_list = list(un_set)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def nearest_dist(points, x, y):
        if not points:
            return 10**9
        best = 10**9
        for px, py in points:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = -10**18
    best_move = (0, 0)

    # Heuristic: push into unclaimed and especially into opponent territory when it is close,
    # but avoid moving toward opponent too much unless it also captures.
    opp_pts = opp_list
    un_pts = un_list
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        pos = (nx, ny)
        score = 0

        if pos in self_set:
            score += 2
        elif pos in un_set:
            score += 6
        elif pos in opp_set:
            # Flipping on entry: good if it can swing territory
            score += 10

        # Prefer moves that create distance from opponent (unless capturing), to resist edge-claims.
        d_opp = nearest_dist(opp_pts, nx, ny)
        if pos in opp_set:
            score += 2  # capturing overrides distance
        else:
            score += 0.8 * d_opp

        # Also bias toward expanding into nearby unclaimed.
        d_un = nearest_dist(un_pts, nx, ny)
        score += 0.6 * (20 - min(d_un, 20))

        # Tie-break deterministically by move ordering and then position.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]