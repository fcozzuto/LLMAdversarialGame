def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    w, h = int(observation.get("grid_width", 8)), int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    res = [(int(r[0]), int(r[1])) for r in resources]
    # Deterministic order for tie-breaking
    res.sort()

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Evaluate next-step moves: prefer resources where we are closer than opponent,
    # otherwise block by moving toward resources the opponent is likely to take.
    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        my_pos = (nx, ny)

        val = 0
        for i, r in enumerate(res):
            d_me = dist(my_pos, r)
            d_op = dist((ox, oy), r)
            # If we can reach this resource sooner or at same time, it is high value.
            # Otherwise, treat it as an "opportunity cost" to deny.
            if d_me < d_op:
                val += 1000 - 10 * d_me - 2 * i
            elif d_me == d_op:
                val += 200 - 5 * d_me - i
            else:
                # Move that makes us closer than opponent is still encouraged a bit
                # to potentially swing next turn.
                gap = d_op - d_me
                if gap > 0:
                    val += 50 + gap - i
                # Softly bias toward reducing opponent's nearest reach
                val -= (d_me - d_op)

        # Small preference for not worsening our proximity to all resources (keeps momentum)
        cur_score = 0
        for i, r in enumerate(res[:6]):
            cur_score += dist((sx, sy), r) + 0.1 * i
        nxt_score = 0
        for i, r in enumerate(res[:6]):
            nxt_score += dist(my_pos, r) + 0.1 * i
        val -= 2 * (nxt_score - cur_score)

        # Deterministic tie-break: prefer staying or lexicographically smaller move deltas
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]