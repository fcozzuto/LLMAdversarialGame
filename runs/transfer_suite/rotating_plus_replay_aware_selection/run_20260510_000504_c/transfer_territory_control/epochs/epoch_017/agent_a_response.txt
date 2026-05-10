def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation.get("opponent_position") or (sx, sy)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist_to_set(x, y, s):
        if not s: return abs(x - ox) + abs(y - oy)
        best = 10**9
        for px, py in s:
            d = abs(x - px) + abs(y - py)
            if d < best: best = d
        return best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_front = opp_terr if opp_terr else {(ox, oy)}
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in opp_terr:
            base = 50.0
        elif (nx, ny) in unclaimed:
            base = 18.0
        elif (nx, ny) in self_terr:
            base = 4.0
        else:
            base = 1.0

        d_opp = dist_to_set(nx, ny, opp_front)
        near_opp = 10.0 / (1 + d_opp)  # prefer pushing into opponent-controlled/unclaimed clusters

        # small bias to stay moving generally toward opponent
        adv = (-(abs(nx - ox) + abs(ny - oy)) / 50.0)

        val = base + near_opp + adv
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    # Fallback: if all moves blocked, stay
    return best_move