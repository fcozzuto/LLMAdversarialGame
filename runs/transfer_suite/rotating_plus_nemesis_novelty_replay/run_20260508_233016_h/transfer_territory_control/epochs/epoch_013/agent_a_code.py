def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_pos = tuple(observation["opponent_position"])
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(a, b):
        d = a - b
        return d if d >= 0 else -d

    unclaimed_list = list(unclaimed)
    if unclaimed_list:
        # Nearest unclaimed to current position for global pressure direction
        nx, ny = min(unclaimed_list, key=lambda c: md(c[0], sx) + md(c[1], sy))
        base_dist_unclaimed = md(nx, sx) + md(ny, sy)
    else:
        base_dist_unclaimed = 99

    def best_unclaimed_dist_to(x, y):
        if not unclaimed_list:
            return 0
        return min(md(x, cx) + md(y, cy) for cx, cy in unclaimed_list)

    best = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        cell = (nx, ny)
        dist_op = md(cell[0], opp_pos[0]) + md(cell[1], opp_pos[1])
        dist_to_nearest_unclaimed = best_unclaimed_dist_to(nx, ny) if unclaimed_list else 0

        if cell in unclaimed:
            gain = 2
        elif cell in opp_terr:
            gain = 4
        elif cell in self_terr:
            gain = 0
        else:
            gain = 1  # stepping onto some other untracked cell shouldn't happen often

        # Expand while staying away from counter-claim pressure; tie-break deterministically by coordinates.
        score = gain * 10 + dist_op * 0.35 - dist_to_nearest_unclaimed * 0.15
        # Small bias to continue expansion direction when unclaimed exists
        if unclaimed_list:
            cur_unclaimed_dist = base_dist_unclaimed
            next_unclaimed_dist = dist_to_nearest_unclaimed
            score += (cur_unclaimed_dist - next_unclaimed_dist) * 0.6

        if (score, -nx, -ny) > (best[0], best[1], best[2]):
            best = (score, -nx, -ny)
            best_move = [dx, dy]

    return best_move