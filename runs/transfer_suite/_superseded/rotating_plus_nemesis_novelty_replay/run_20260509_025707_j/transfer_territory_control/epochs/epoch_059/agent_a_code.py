def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    self_set = observation.get("self_territory") or []
    opp_set = observation.get("opponent_territory") or []
    self_cnt = observation.get("self_territory_count", len(self_set))
    opp_cnt = observation.get("opponent_territory_count", len(opp_set))

    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed_set = set((p[0], p[1]) for p in unclaimed) if unclaimed else set()

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    aggressive = self_cnt <= opp_cnt
    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        bonus = 1 if (nx, ny) in unclaimed_set else 0
        score = (-d if aggressive else d) + 2 * bonus
        if best is None or score > best_score or (score == best_score and (dx, dy) == (0, 0)):
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]