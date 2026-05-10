def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in role) or ("hunter" in role) or ("chaser" in role)
    # If role unclear, use score comparison heuristic (pursuer should try to capture)
    if not pursuer:
        s = observation.get("scores", {}) or {}
        if isinstance(s, dict):
            a = s.get("self", s.get("me", s.get("player", 0)))
            b = s.get("opponent", s.get("op", s.get("enemy", 0)))
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                pursuer = a < b  # we are behind -> likely pursuer trying to gain capture points

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def passable(x, y):
        return inb(x, y) and (x, y) not in blocked

    def dist_after(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            return None
        # Chebyshev distance corresponds to minimal king-move steps to same cell with diagonals
        return max(abs(nx - ox), abs(ny - oy))

    # Candidate scoring: pursuer minimizes distance; evader maximizes distance with corner/edge pressure.
    best = None
    best_score = None
    # Deterministic tie-breaking: fixed iteration order, then lexicographic on (dx,dy).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue
        d = max(abs(nx - ox), abs(ny - oy))
        if pursuer:
            # Also penalize moving away from opponent in L1 to reduce zigzag effectiveness
            score = (-d, -(abs(nx - ox) + abs(ny - oy)))
        else:
            # Move away; prefer corners (maximize min-distance to edges) to avoid getting funneled
            edge = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
            corner = (nx in (0, w - 1)) and (ny in (0, h - 1))
            score = (d, edge, 1 if corner else 0)
        if best is None:
            best = [dx, dy]
            best_score = score
        else:
            if pursuer:
                if score > best_score:
                    best_score = score
                    best = [dx, dy]
            else:
                if score > best_score:
                    best_score = score
                    best = [dx, dy]
    return best if best is not None else [0, 0]