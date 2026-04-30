def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    obst = set((p[0], p[1]) for p in obstacles)
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        def dist(a, b, c, d):
            dx = a - c
            dy = b - d
            return (dx * dx + dy * dy)
        best = None
        for rx, ry in resources:
            if (rx, ry) in obst:
                continue
            ds = dist(x, y, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Prefer resources we're closer to than opponent; add slight preference for closeness
            score = (ds - do) * 1000 + ds
            # Also nudge away from being trapped: penalize being far from any resource after committing
            if best is None or score < best[0] or (score == best[0] and (rx, ry) < best[1]):
                best = (score, (rx, ry))
        tx, ty = best[1]
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        d_to_target = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        # Block contest: if opponent is closer to the target, prioritize moves that reduce opponent's advantage
        d_opp_to_target = (ox - tx) * (ox - tx) + (oy - ty) * (oy - ty)
        d_opp_next = d_opp_to_target  # unknown opponent move; use a conservative heuristic
        val = d_to_target - (d_opp_next - d_to_target) * 0  # keep deterministic but stable
        # If stepping onto a resource, strongly prefer
        if (nx, ny) in set((r[0], r[1]) for r in resources):
            val -= 10**9
        # Slightly avoid adjacency to opponent to reduce being contested (when not targeting immediate pickup)
        man = abs(nx - ox) + abs(ny - oy)
        if man <= 1 and (nx, ny) != (tx, ty):
            val += 50
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]