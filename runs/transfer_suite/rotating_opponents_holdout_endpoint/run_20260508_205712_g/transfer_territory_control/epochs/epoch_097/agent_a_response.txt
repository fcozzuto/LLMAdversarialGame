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

    def interiorness(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    def adj_count(a, target_set):
        x, y = a
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in target_set:
                    cnt += 1
        return cnt

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (float("-inf"), 0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            score = -1000
        else:
            score = 0.0
            if (nx, ny) in self_t:
                score += 2.0 + 0.15 * interiorness(nx, ny)
            elif (nx, ny) in unclaimed:
                score += 6.0 + 0.8 * adj_count((nx, ny), self_t) - 0.2 * adj_count((nx, ny), opp_t)
            elif (nx, ny) in opp_t:
                score += 7.0 + 1.0 * adj_count((nx, ny), self_t) + 0.3 * adj_count((nx, ny), opp_t)
            else:
                score += 0.2 * adj_count((nx, ny), self_t)

            md_opp = abs(nx - ox) + abs(ny - oy)
            score += -0.04 * md_opp
        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]