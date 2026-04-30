def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [7, 7]) or [7, 7]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my = (sx, sy)
    opp = (ox, oy)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    if not resources:
        # retreat from opponent to farthest corner-like direction
        best = None
        bestv = -10**9
        for dx, dy, nx, ny in moves:
            v = dist((nx, ny), opp) - 0.2 * min(nx, ny) - 0.2 * min(w - 1 - nx, h - 1 - ny)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    # Choose target resource where we have a tempo advantage; prefer safer approach
    best_target = resources[0]
    best_score = -10**18
    for r in resources:
        dm = dist(my, r)
        do = dist(opp, r)
        # If opponent is much closer, deprioritize strongly.
        tempo = (do - dm)
        s = 2.0 * tempo - 0.08 * dm
        if s > best_score:
            best_score = s
            best_target = r

    tx, ty = best_target
    # One-step policy: move that improves distance to chosen target while avoiding proximity/overcommit to opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in moves:
        d_to_target = dist((nx, ny), best_target)
        d_to_opp = dist((nx, ny), opp)
        # Keep some separation; if opponent is close, prioritize increasing separation.
        separation_term = 0.35 * d_to_opp if d_to_opp <= 4 else 0.05 * d_to_opp
        val = -d_to_target + separation_term
        if (nx, ny) == best_target:
            val += 1e6  # grabbing is dominant if visible
        # Mild tie-break toward lower coordinates deterministically
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]