def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_evader = ("evad" in self_role) or ("runner" in self_role) or ("evasion" in self_role) or (self_role == "evader")
    opp_evader = ("evad" in opp_role) or ("runner" in opp_role) or ("evasion" in opp_role) or (opp_role == "evader")
    pursue = (not self_evader) or opp_evader

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    def penalty_adj(nx, ny):
        # small deterrent from squeezing into obstacle corners/walls
        pen = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            if (nx + dx, ny + dy) in obs:
                pen += 1
        return pen

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        dist = max(abs(nx - ox), abs(ny - oy))  # diagonal distance proxy
        pen = penalty_adj(nx, ny)

        # If pursuing: minimize distance, then minimize penalty, then deterministic tie-break.
        # If evading: maximize distance, then minimize penalty.
        key = (dist, pen) if pursue else (-dist, pen)

        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]
        elif key == best_key:
            # deterministic: keep earlier move in 'moves' order (current best wins)

            pass

    return best if best is not None else [0, 0]