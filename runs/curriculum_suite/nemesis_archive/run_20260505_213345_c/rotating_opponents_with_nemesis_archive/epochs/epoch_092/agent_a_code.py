def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist8(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    # Pick a resource where we have a favorable race (reach sooner than opponent).
    # If none, pick the one that reduces the opponent's advantage the most.
    candidates = []
    for r in resources:
        d_me = dist8((sx, sy), r)
        d_opp = dist8((ox, oy), r)
        advantage = d_opp - d_me  # positive: we reach sooner
        candidates.append((advantage, d_me, d_opp, r))
    candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3][0], t[3][1]))
    target = candidates[0][3]

    # Intercept/avoid: choose move that gets closer to target, but also maximizes
    # our future advantage vs opponent for that same target; penalize stepping into obstacles/off-grid.
    best_score = -10**18
    best_move = (0, 0)
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d_me_next = dist8((nx, ny), target)
        d_opp_to_target = dist8((ox, oy), target)

        # Main: maximize advantage for the next step.
        score = (d_opp_to_target - d_me_next) * 1000

        # Secondary: encourage progress; discourage wandering.
        score += -d_me_next

        # If the move reaches/collects target, strongly prefer it.
        if (nx, ny) == target:
            score += 10**6

        # Minor tie-break: deterministic preference ordering already via best_move updates.
        if score > best_score:
            best_score = score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]