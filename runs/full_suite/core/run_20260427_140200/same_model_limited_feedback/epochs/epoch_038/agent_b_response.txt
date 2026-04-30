def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        # Fallback: move away from opponent while staying safe
        best = None
        bestv = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            # Prefer moving that increases Chebyshev distance
            dv = max(abs(nx - ox), abs(ny - oy))
            if dv > bestv:
                bestv = dv
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev on 8-neighbor grid

    # Choose a target resource that we can reach relatively sooner than opponent
    best_res = None
    best_score = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Reward being closer; penalize if opponent is closer
        score = (do - ds) * 10 - ds
        # Slightly prefer closer overall to reduce dithering
        if score > best_score:
            best_score = score
            best_res = (rx, ry)

    tx, ty = best_res

    # Evaluate immediate moves: progress to target + safety vs opponent + avoid obstacles
    best = (0, 0)
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_to_t = dist((nx, ny), (tx, ty))
        d_from_o = dist((nx, ny), (ox, oy))
        # Avoid getting too close if it allows immediate steal
        # (If opponent is adjacent, staying away matters more.)
        opp_adj = 1 if dist((ox, oy), (nx, ny)) <= 1 else 0
        v = -d_to_t * 8 + d_from_o * 3 - opp_adj * 12
        # Also discourage oscillation a bit using turn_index and position (deterministic, no memory)
        v -= ((observation.get("turn_index", 0) + nx * 7 + ny * 13) % 5) * 0.01
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]