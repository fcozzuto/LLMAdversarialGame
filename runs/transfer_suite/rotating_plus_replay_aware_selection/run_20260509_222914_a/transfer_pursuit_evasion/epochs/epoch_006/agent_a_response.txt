def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    role = observation.get("self_role", "pursuer")
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corners = [c for c in corners if c not in obstacles] or [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def d_cheb(a, b):
        ax, ay = a
        bx, by = b
        da = ax - bx
        db = ay - by
        return abs(da) if abs(da) > abs(db) else abs(db)

    self_pt = (x, y)
    opp_pt = (ox, oy)
    target_corner = None
    if role != "pursuer":
        target_corner = max(corners, key=lambda c: d_cheb(c, self_pt))
    else:
        # pursuer: prefer moves that reduce distance, but also subtly head toward the corner opposite opponent
        target_corner = min(corners, key=lambda c: d_cheb(c, opp_pt))

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        np = (nx, ny)
        dist_opp = d_cheb(np, opp_pt)
        # small wall/corner bias via distance to chosen corner
        dist_corner = d_cheb(np, target_corner) if target_corner is not None else 0
        # score: pursuer minimize dist_opp; evader maximize dist_opp and distance from opponent
        if role == "pursuer":
            score = -dist_opp * 1000 - dist_corner
        else:
            score = dist_opp * 1000 + dist_corner
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    return [best[0], best[1]] if best is not None else [0, 0]