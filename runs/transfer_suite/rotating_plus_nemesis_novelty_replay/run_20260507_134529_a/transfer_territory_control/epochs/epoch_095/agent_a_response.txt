def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    self_cnt = int(observation.get("self_territory_count", len(self_terr)) or len(self_terr))
    opp_cnt = int(observation.get("opponent_territory_count", len(opp_terr)) or len(opp_terr))
    turn = int(observation.get("turn_index", 0) or 0)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -1e18
    my_dist = abs(sx - ox) + abs(sy - oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            val = -1e18
        else:
            val = 0.0
            if (nx, ny) in opp_terr:
                swing = 7.0 if opp_cnt >= self_cnt else 5.0
                val += swing + 0.2
            elif (nx, ny) in unclaimed:
                val += 3.2
            elif (nx, ny) in self_terr:
                val += 0.9
            else:
                val += 0.4

            if (nx, ny) in resources:
                val += 3.0

            # Prefer reducing distance to opponent early; prefer distancing if we are behind.
            nd = abs(nx - ox) + abs(ny - oy)
            if opp_cnt > self_cnt:
                val += (nd - my_dist) * 0.15  # back off when behind (safer)
            else:
                val += (my_dist - nd) * 0.12  # press when ahead

            # Avoid stepping into likely contested chokepoints near opponent.
            if nd <= 2 and opp_cnt > self_cnt:
                val -= 2.0
            if nd <= 1 and (nx, ny) in unclaimed and opp_cnt > self_cnt:
                val -= 1.2

            # Small deterministic tie-breaker: rotate preference by turn parity.
            val += (dx * 3 + dy * 5 + (turn & 1)) * 0.001

        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]