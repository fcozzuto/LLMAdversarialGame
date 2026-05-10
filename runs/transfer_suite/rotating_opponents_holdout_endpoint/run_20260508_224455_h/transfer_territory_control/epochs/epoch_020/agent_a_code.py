def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def neigh8_list(x, y):
        out = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        out.append((nx, ny))
        return out

    def adj_to_opp(c):
        x, y = c
        for nx, ny in neigh8_list(x, y):
            if (nx, ny) in opp_t:
                return True
        return False

    edge_unclaimed = [c for c in unclaimed if adj_to_opp(c)]
    if edge_unclaimed:
        target = min(edge_unclaimed, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), c[0], c[1]))
    elif opp_t:
        target = min(opp_t, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), c[0], c[1]))
    else:
        target = (sx, sy)

    tx, ty = target
    best_score, best_move = -10**18, (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        is_self = (nx, ny) in self_t
        is_opp = (nx, ny) in opp_t
        is_un = (nx, ny) in unclaimed

        neigh = neigh8_list(nx, ny)
        cnt_un = sum(1 for p in neigh if p in unclaimed)
        cnt_opp = sum(1 for p in neigh if p in opp_t)
        cnt_self = sum(1 for p in neigh if p in self_t)

        # Prefer pressing opponent edge, expand into unclaimed, and opportunistically flip opponent cells.
        score = 0
        if is_opp:
            score += 60
            score += 3 * cnt_opp + 1 * cnt_un
        elif is_un:
            score += 35
            score += 3 * cnt_un + 2 * cnt_opp
        elif is_self:
            score += 8
            score += 2 * cnt_self + 1 * cnt_opp

        dist_now = abs(nx - tx) + abs(ny - ty)
        dist_prev = abs(sx - tx) + abs(sy - ty)
        score += 6 * (dist_prev - dist_now)  # move closer to target

        # Avoid wasting moves into isolated corners: penalize if it doesn't touch anything useful.
        if cnt_un + cnt_opp == 0:
            score -= 18

        # Tiny deterministic tie-break: lower dx then dy magnitude.
        score -= (abs(dx) * 0.01 + abs(dy) * 0.001)

        if score > best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]