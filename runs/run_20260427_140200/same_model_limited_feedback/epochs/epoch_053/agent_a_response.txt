def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                if (nx, ny) not in obstacles:
                    moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def cheb(a, b):
        return abs(a[0] - b[0]) if False else max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    me = (sx, sy)
    them = (ox, oy)

    best_res = None
    best_key = None
    for r in resources:
        drm = dist(me, r)
        dro = dist(them, r)
        # Prefer resources we can reach sooner, otherwise block by pushing closer to contested ones
        key = (0 if drm <= dro else 1, drm - dro, drm)
        if best_key is None or key < best_key:
            best_key = key
            best_res = r
    if best_res is None:
        return [0, 0]

    # Evaluate candidate moves with a small, deterministic scoring
    target = best_res
    opp_candidates = [r for r in resources if dist(them, r) <= dist(me, r)]
    opp_target = opp_candidates[0] if opp_candidates else target

    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        me2 = (nx, ny)
        my = -dist(me2, target)  # closer to target is better
        # If opponent is closer to their chosen resource, try to pull away or interfere by moving toward the conflict line
        op = -dist(them, opp_target)
        # Penalize moves that get too close to opponent (avoid enabling races)
        close_pen = -2 * (0 if dist(me2, them) > 1 else 1)
        # Mild preference for heading toward the board center to reduce being trapped by corner races
        center = (w//2, h//2)
        cen = -0.15 * dist(me2, center)
        score = 3.0 * my + 1.0 * op + close_pen + cen
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]