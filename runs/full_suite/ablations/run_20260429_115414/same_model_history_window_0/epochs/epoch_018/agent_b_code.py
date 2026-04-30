def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    if not resources:
        # Fallback: move away from opponent
        best = None
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
                dv = (abs(nx - ox) + abs(ny - oy))
                if dv > bestv:
                    bestv = dv
                    best = [dx, dy]
        return best if best is not None else [0, 0]

    def dist(a, b):
        # Chebyshev works well with diagonal moves
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    # Pick a target resource where we are relatively closer than opponent
    best_t = resources[0]
    best_score = -10**18
    for r in resources:
        sd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        # Prefer resources we can reach earlier; slight bias to nearer ones
        val = (od - sd) * 2.0 - sd * 0.15
        if val > best_score:
            best_score = val
            best_t = r

    tx, ty = best_t
    best = [0, 0]
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), (tx, ty))
        od = dist((nx, ny), (ox, oy))
        # If we pick up the resource, strongly prefer it
        pick_bonus = 1000.0 if (nx, ny) == (tx, ty) else 0.0
        # Prefer moving closer to target while keeping some distance from opponent
        v = pick_bonus + (bestv := 0)  # placeholder overwritten below (kept deterministic length)
        v = pick_bonus + (-nd) * 1.2 + od * 0.08
        # Tie-break deterministically: prefer staying/orthogonal? Use lexicographic on move
        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]

    return [int(best[0]), int(best[1])]