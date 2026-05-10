def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    adj8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    base_opp_dist = abs(sx - ox) + abs(sy - oy)

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def neighbors_score(px, py):
        c_self = c_unk = c_opp = 0
        for ax, ay in adj8:
            nx, ny = px + ax, py + ay
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                if (nx, ny) in self_t:
                    c_self += 1
                elif (nx, ny) in opp_t:
                    c_opp += 1
                elif (nx, ny) in unclaimed:
                    c_unk += 1
        return c_self, c_unk, c_opp

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_t:
            score += 2500
        elif (nx, ny) in unclaimed:
            score += 60
        if (nx, ny) in self_t:
            score += 12

        nd_opp = abs(nx - ox) + abs(ny - oy)
        score += (base_opp_dist - nd_opp) * 3

        score += (14 - (abs(nx - cx) + abs(ny - cy))) * 0.8  # contest center

        c_self, c_unk, c_opp = neighbors_score(nx, ny)
        score += c_self * 18 + c_unk * 10
        score += c_opp * 6

        # Prefer expansion over idle when comparable
        if (dx, dy) == (0, 0):
            score -= 25

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]