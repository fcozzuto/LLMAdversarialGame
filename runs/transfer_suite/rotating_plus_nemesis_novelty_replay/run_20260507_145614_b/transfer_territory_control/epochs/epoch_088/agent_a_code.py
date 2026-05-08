def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    my_set = set((p[0], p[1]) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_set = set((p[0], p[1]) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    yield nx, ny

    def count_adj(sset, x, y):
        c = 0
        for nx, ny in neighbors8(x, y):
            if (nx, ny) in sset:
                c += 1
        return c

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    center_dist = abs(sx - cx) + abs(sy - cy)
    opp_adj_weight = 90 if center_dist < (w + h) * 0.35 else 70

    best = None
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in obstacles:
                nx, ny = sx, sy
                dx, dy = 0, 0
            if not (0 <= nx < w and 0 <= ny < h):
                continue

            score = 0
            if (nx, ny) in opp_set:
                score += 1200 + 20 * count_adj(opp_set, nx, ny)
            if (nx, ny) in unclaimed:
                score += 650
            if (nx, ny) in my_set:
                score -= 80

            score += opp_adj_weight * count_adj(opp_set, nx, ny)
            score += 35 * count_adj(my_set, nx, ny)

            score += - (abs(nx - cx) + abs(ny - cy)) * 2.5
            score += 3 * (abs(dx) + abs(dy) == 0)

            if score > best_score:
                best_score = score
                best = (dx, dy)

    return [int(best[0]), int(best[1])]