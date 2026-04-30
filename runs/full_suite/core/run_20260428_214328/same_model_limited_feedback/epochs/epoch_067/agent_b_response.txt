def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def neighbors_free(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                c += 1
        return c

    # If no resources visible, drift toward center to stay competitive.
    if not resources:
        tx, ty = (w - 1) / 2, (h - 1) / 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            score = -abs(nx - tx) - abs(ny - ty) + 0.1 * neighbors_free(nx, ny)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    # Pick a target resource that we can reach with an advantage, otherwise best contest.
    best_t = None
    for r in resources:
        d_self = dist((sx, sy), r)
        d_opp = dist((ox, oy), r)
        advantage = d_opp - d_self
        # Prefer grabbing soon; break ties by stronger advantage and remaining_count if present.
        remain = observation.get("remaining_resource_count", 0)
        score_t = advantage * 2.5 - d_self + (0.2 * remain)
        if best_t is None or score_t > best_t[0]:
            best_t = (score_t, r, d_self, d_opp)
    target = best_t[1]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Primary: get closer to target.
        d1 = dist((nx, ny), target)
        d0 = dist((sx, sy), target)

        # Secondary: deny opponent by maintaining (our - their) distance advantage to target.
        d_opp_next = dist((ox, oy), target)

        # Multi-resource tie-break: prefer moves that improve our best contest across all resources.
        best_adv = -10**9
        for r in resources:
            a = dist((ox, oy), r) - dist((nx, ny), r)
            if a > best_adv:
                best_adv = a

        # Tertiary: avoid dead-ends / obstacle hugging.
        free = neighbors_free(nx, ny)

        # If we're already on a resource tile, prioritize staying secure (still move allowed but less likely).
        on_res = 1 if (nx, ny) in set(tuple(p) for p in resources) else 0

        score = (-d1) + (d0 - d1) * 0.8 + best_adv * 1.2 + free * 0.05 + on_res * 0.3
        # Small penalty for moving away from target.
        if d1 > d0:
            score -= (d1 - d0) * 0.7

        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]