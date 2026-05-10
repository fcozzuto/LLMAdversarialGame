def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    self_terr = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_terr = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a goal: attack opponent if we're behind, else expand toward unclaimed.
    myc = observation.get("self_territory_count", len(self_terr))
    opc = observation.get("opponent_territory_count", len(opp_terr))
    attack = myc < opc or (observation.get("turn_index", 0) % 10 < 6)

    opp_list = list(opp_terr)
    un_list = list(unclaimed)

    def nearest_dist_to_set(x, y, arr):
        if not arr:
            return 999
        best = 999
        for (tx, ty) in arr:
            d = manh(x, y, tx, ty)
            if d < best:
                best = d
        return best

    # Frontier preference: move that reduces distance to opponent territory (attack) or unclaimed (expand).
    target_arr = opp_list if attack else un_list

    best_move = (0, 0)
    best_score = -10**9
    t = observation.get("turn_index", 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        cell = (nx, ny)
        score = 0

        # Direct capture value (enter opponent-owned flips).
        if cell in opp_terr:
            score += 1200

        # Expansion value.
        if cell in unclaimed:
            score += 220

        # Staying on our territory is neutral/slightly positive (avoid hemorrhage).
        if cell in self_terr:
            score += 30

        # Avoid stepping adjacent to obstacles (gets you stuck behind them vs sweepers).
        adj_obs = 0
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                if ox == 0 and oy == 0:
                    continue
                if (nx + ox, ny + oy) in obstacles:
                    adj_obs += 1
        score -= 5 * adj_obs

        # Move toward goal (deterministic tie-break by considering score + direction bias).
        d_goal = nearest_dist_to_set(nx, ny, target_arr)
        score -= 8 * d_goal

        # Small bias to break ties differently across time (deterministic).
        score += (dx * 2 - dy) * (1 if (t % 2 == 0) else -1)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]