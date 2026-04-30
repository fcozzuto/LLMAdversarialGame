def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))

    if not resources:
        return [0, 0]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Pick a resource where we have relative advantage; if not, pick one that hurts opponent least.
    best = None
    for rx, ry in resources:
        ds = dist2((sx, sy), (rx, ry))
        do = dist2((ox, oy), (rx, ry))
        advantage = (do - ds)  # positive means we're closer
        # Adaptation: change objective to be more opponent-aware than simple nearest.
        value = advantage * 10 - ds * 0.1
        if best is None or value > best[0] or (value == best[0] and (ds < best[2])):
            best = (value, (rx, ry), ds)

    tx, ty = best[1]

    # Greedy step towards target with obstacle avoidance; deterministic tie-breaking.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < observation["grid_width"] and 0 <= ny < observation["grid_height"]):
            continue
        if (nx, ny) in obstacles:
            continue
        ns = dist2((nx, ny), (tx, ty))
        # Also softly avoid moving closer to opponent when we are not clearly winning.
        do_next = dist2((nx, ny), (ox, oy))
        opp_weight = 0.05 if best[0] <= 0 else 0.02
        score = ns - opp_weight * do_next
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]