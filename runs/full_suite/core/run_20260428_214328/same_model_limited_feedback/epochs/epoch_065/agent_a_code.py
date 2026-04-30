def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    grid_w = observation.get("grid_width", 8)
    grid_h = observation.get("grid_height", 8)

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev for 8-dir moves

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_res = None
    best_adv = -10**9
    best_tiebreak = 10**9
    epoch = observation.get("turn_index", 0)
    flip = (epoch // 2) % 2

    for i, r in enumerate(resources):
        rx, ry = r
        myd = dist((x, y), (rx, ry))
        opd = dist((ox, oy), (rx, ry))
        adv = opd - myd
        # deterministic tie-break changes materially over time
        tiebreak = (rx + 3 * ry + (1 if flip else 0) * i) % 11
        if adv > best_adv or (adv == best_adv and tiebreak < best_tiebreak):
            best_adv = adv
            best_res = (rx, ry)
            best_tiebreak = tiebreak

    if not best_res:
        # fallback: avoid obstacles and step away from opponent if possible
        candidates = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if nx < 0 or ny < 0 or nx >= grid_w or ny >= grid_h:
                continue
            if (nx, ny) in obstacles:
                continue
            candidates.append((dist((nx, ny), (ox, oy)), dx, dy))
        candidates.sort(reverse=True)
        return [candidates[0][1], candidates[0][2]] if candidates else [0, 0]

    rx, ry = best_res
    avoid_opponent = (observation.get("turn_index", 0) % 3 == 0)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if nx < 0 or ny < 0 or nx >= grid_w or ny >= grid_h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = dist((nx, ny), (rx, ry))
        # simulate opponent responsiveness: if opponent is closer to this resource, prefer further from opponent
        opd2 = dist((ox, oy), (rx, ry))
        score = (best_adv * 5) - myd2 * 3 + (opd2 - myd2) * 4
        if avoid_opponent:
            score += dist((nx, ny), (ox, oy)) * 1.5
        # discourage staying unless forced
        if dx == 0 and dy == 0:
            score -= 2.0
        # deterministic nudge: bias by direction to avoid loops
        score += (dx * 0.01 - dy * 0.007) * ((epoch := observation.get("turn_index", 0)) % 5 + 1)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]