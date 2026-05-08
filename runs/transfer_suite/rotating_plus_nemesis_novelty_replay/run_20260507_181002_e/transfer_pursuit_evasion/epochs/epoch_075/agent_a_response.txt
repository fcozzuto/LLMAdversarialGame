def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    self_is_pursuer = ("pursuer" in sr) or ("chaser" in sr) or ("seeker" in sr) or ("hunter" in sr)
    # If role unknown, default to pursuer-like behavior (best against pursuit_direct).
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Deterministic tie-breaker: prefer not staying if score ties, then lexicographic.
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist = d2(nx, ny, ox, oy)
        # Pursuer minimizes distance; evader maximizes distance.
        score = dist if not self_is_pursuer else -dist
        # Additional obstacle-aware nudge: prefer moves with more legal neighbors.
        neigh = 0
        for ddx, ddy in moves:
            mx, my = nx + ddx, ny + ddy
            if legal(mx, my):
                neigh += 1
        score = score + (neigh * (1 if not self_is_pursuer else -0.5))
        # Tie-break
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score and best is not None:
            stay = (best[0] == 0 and best[1] == 0)
            cand_stay = (dx == 0 and dy == 0)
            if stay and not cand_stay:
                best = (dx, dy)
            elif cand_stay == stay:
                if (dx, dy) < best:
                    best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]