def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    def toset(v):
        s = set()
        if v:
            for p in v:
                if p and len(p) >= 2:
                    s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    if not unclaimed:
        unclaimed = toset(observation.get("resources"))
    resources = toset(observation.get("resources"))

    opp_prev = toset(observation.get("opponent_path"))
    if not opp_prev:
        opp_prev = toset(observation.get("opponent_territory"))

    best = None
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            # base: prefer moves that expand into unclaimed/resources; otherwise keep distance
            if unclaimed:
                target_dist = min(abs(nx - x) + abs(ny - y) for (x, y) in unclaimed if 0 <= x < w and 0 <= y < h)
            elif resources:
                target_dist = min(abs(nx - x) + abs(ny - y) for (x, y) in resources)
            else:
                target_dist = 10**6

            opp_dist = abs(nx - ox) + abs(ny - oy)
            score = 0
            score += (10**4 - target_dist)  # smaller dist to target is better
            score += 50 * opp_dist          # stay away from opponent
            if (nx, ny) in unclaimed:
                score += 5000
            if (nx, ny) in resources:
                score += 2000
            # slight penalty near opponent's recent/known area
            if opp_prev and (nx, ny) in opp_prev:
                score -= 800
            # mild center bias for determinism/stability
            score -= (abs(nx - (w // 2)) + abs(ny - (h // 2)))

            if score > best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]