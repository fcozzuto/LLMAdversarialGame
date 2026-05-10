def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for c in observation.get(key) or []:
            if c and len(c) >= 2:
                x, y = int(c[0]), int(c[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    self_t = to_set("self_territory")
    opp_t = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def interiorness(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = -10**18
    best_move = [0, 0]

    def adj_to_opp(x, y):
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_t:
                    cnt += 1
        return cnt

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny = sx, sy  # invalid move -> engine keeps agent in place
        score = 0
        score += 2.0 * interiorness(nx, ny)
        score += -0.8 * (((nx - cx) ** 2 + (ny - cy) ** 2) ** 0.5)

        if (nx, ny) in opp_t:
            score += 6.0
        elif (nx, ny) in self_t:
            score += -1.5
        else:
            score += 2.0

        if (nx, ny) in unclaimed:
            score += 2.5

        score += 0.8 * adj_to_opp(nx, ny)
        score += 0.15 * (abs(nx - ox) + abs(ny - oy)) * (-1)  # slight pull toward opponent direction

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move