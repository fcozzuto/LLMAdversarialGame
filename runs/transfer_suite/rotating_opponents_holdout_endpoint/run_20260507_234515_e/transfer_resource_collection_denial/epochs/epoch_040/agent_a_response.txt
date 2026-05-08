def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cd(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    # Score each move by our best "win resource" advantage after moving.
    best_move = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Prefer taking a resource where we are closer than opponent (or least behind).
        # Tie-break: prefer nearer self distance, then tie-break by lexicographic move.
        chosen = None
        for rx, ry in resources:
            self_d = cd((nx, ny), (rx, ry))
            opp_d = cd((ox, oy), (rx, ry))
            adv = opp_d - self_d  # positive means we can likely take first
            # Create a comparable tuple: maximize adv, then minimize self_d, then prefer closer to opponent's side less.
            # Also discourage picking resources that are closer to opponent than us.
            score = (adv, -self_d, -(rx + ry))
            if chosen is None or score > chosen[0]:
                chosen = (score, self_d, (rx, ry))
        if chosen is None:
            # No resources visible: go toward center deterministically.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dist = abs(nx - cx) + abs(ny - cy)
            move_score = (-dist, -dx, -dy)
        else:
            move_score = (chosen[0][0], chosen[0][1], chosen[0][2], -dx, -dy)
        if best_score is None or move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]