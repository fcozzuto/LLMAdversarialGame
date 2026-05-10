def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    resources = set(tuple(p) for p in (observation.get("resources") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    best = [0, 0]
    best_score = -10**18

    # If we are far behind, focus on fastest expansion; otherwise protect distance from opponent.
    gap = (observation.get("scores", {}).get(observation.get("self_name"), 0) -
           observation.get("scores", {}).get(observation.get("opponent_name"), 0)) if isinstance(observation.get("scores"), dict) else 0
    expansion_bias = 10 if gap < 0 else 0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        # Claiming value
        if (nx, ny) in unclaimed:
            score += 12 + expansion_bias
        if (nx, ny) in resources:
            score += 8

        # Center control
        score += (w + h) - man(nx, ny, cx, cy)

        # Opponent pressure: counterclaiming opponent means avoid proximity; also, if they are very close, prioritize escape.
        d_opp = man(nx, ny, ox, oy)
        if d_opp <= 1:
            score -= 300
        else:
            score += 6 * d_opp

        # Prefer moves that increase our distance from opponent and decrease opponent distance to the center less
        score += (man(sx, sy, ox, oy) - d_opp) * 3
        # Small preference for progress when staying unthreatened
        if d_opp > 2:
            score += (man(sx, sy, cx, cy) - man(nx, ny, cx, cy))

        # Deterministic tie-break: prefer lexicographically smallest (dx,dy)
        if score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
            best_score = score
            best = [dx, dy]

    return best