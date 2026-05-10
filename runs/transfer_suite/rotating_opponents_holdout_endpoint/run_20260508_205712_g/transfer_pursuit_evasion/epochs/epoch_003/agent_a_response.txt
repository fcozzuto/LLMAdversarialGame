def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    x, y = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    self_role = (observation.get("self_role", "") or "").lower()
    obstacles = observation.get("obstacles", []) or []
    obs_set = {(int(a[0]), int(a[1])) for a in obstacles if len(a) >= 2}

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set

    def score_my(newx, newy, want):  # want=+1 evader, want=-1 pursuer
        # One-step minimax: after our move, opponent moves; we evaluate worst-case.
        best = None
        for ddx, ddy in deltas:
            nx2, ny2 = newx + ddx, newy + ddy
            if not valid(nx2, ny2):
                nx2, ny2 = newx, newy
            d = (nx2 - ox) * (nx2 - ox) + (ny2 - oy) * (ny2 - oy)
            # For pursuer, minimize opponent distance; for evader, maximize.
            val = d if want == 1 else -d
            if best is None or (val > best if want == 1 else val > best):
                best = val
        return best if best is not None else (0 if want == 1 else 0)

    # Determine our role
    pursuer = ("purs" in self_role) or ("hunter" in self_role) or ("catch" in self_role)
    want = -1 if pursuer else 1

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            nx, ny = x, y
        # Evaluate from our perspective: for pursuer minimize distance to opponent; for evader maximize.
        worst = None
        for odx, ody in deltas:
            ox2, oy2 = ox + odx, oy + ody
            if not (0 <= ox2 < w and 0 <= oy2 < h and (ox2, oy2) not in obs_set):
                ox2, oy2 = ox, oy
            d = (nx - ox2) * (nx - ox2) + (ny - oy2) * (ny - oy2)
            val = d if not pursuer else -d
            if worst is None or val < worst:
                worst = val
        # Tie-break: prefer moves that reduce opponent escape (for pursuer) or increase (for evader)
        edge = (min(nx, w - 1 - nx) + min(ny, h - 1 - ny))
        if best_val is None or (worst > best_val if want == 1 else worst > best_val) or (worst == best_val and (edge < (best_edge := 0) if pursuer else edge > 0)):
            best_val = worst
            best_move = [dx, dy]

    # Extra deterministic fallback: if something odd happened, go toward/away from opponent avoiding obstacles.
    if best_move == [0, 0] and not any(valid(x + dx, y + dy) for dx, dy in deltas):
        return [0, 0]
    return best_move