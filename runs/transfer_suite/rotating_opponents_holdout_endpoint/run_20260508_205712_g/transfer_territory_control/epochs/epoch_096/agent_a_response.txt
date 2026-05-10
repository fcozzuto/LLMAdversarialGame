def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or [0, 0])
    ox, oy = map(int, observation.get("opponent_position") or [w - 1, h - 1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

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

    def interiorness(x, y):
        d = min(x, y, w - 1 - x, h - 1 - y)
        return d  # bigger => more interior

    def adj_count(a, target_set):
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = a[0] + dx, a[1] + dy
                if (nx, ny) in target_set:
                    cnt += 1
        return cnt

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    opp_adj = adj_count((sx, sy), opp_t)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue

        cell = (nx, ny)
        in_opp = cell in opp_t
        in_un = cell in unclaimed
        in_self = cell in self_t

        dist_to_opp = max(1, abs(nx - ox) + abs(ny - oy))
        border_bias = -abs(interiorness(nx, ny) - 2)  # avoid hugging too close to border late-game

        score = 0
        if in_un:
            score += 30 + 4 * interiorness(nx, ny) + border_bias
        elif in_opp:
            score += 45 + 5 * interiorness(nx, ny) + 2 * adj_count(cell, self_t)
            score -= 8 // dist_to_opp
            score -= 3 if opp_adj >= 2 else 0
        elif in_self:
            score += 6 + 2 * interiorness(nx, ny) - (2 if (nx + ny) % 2 == 1 else 0)
        else:
            score += 10 + 3 * interiorness(nx, ny)

        # small preference for progressing inward deterministically
        score += 1 if interiorness(nx, ny) > interiorness(sx, sy) else 0
        score -= 1 if interiorness(nx, ny) < interiorness(sx, sy) else 0

        if score > best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]