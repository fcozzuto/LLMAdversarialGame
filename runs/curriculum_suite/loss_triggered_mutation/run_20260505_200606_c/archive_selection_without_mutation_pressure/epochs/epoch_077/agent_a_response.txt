def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if w <= 0 or h <= 0 or not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Choose a resource that I'm relatively closer to (interceptor/opportunistic).
    best_rx, best_ry = None, None
    best_adv = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        # Prefer resources with high advantage; slight tie-break toward closer overall.
        adv = (opd - myd) * 10 - (myd)
        if best_adv is None or adv > best_adv:
            best_adv = adv
            best_rx, best_ry = rx, ry

    if best_rx is None:
        return [0, 0]

    # Evaluate immediate move toward chosen resource, with repulsion from opponent and walls.
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = dist(nx, ny, best_rx, best_ry)
        target_bonus = -myd
        # If opponent is very close to the target, avoid giving it a direct approach.
        opd = dist(ox, oy, best_rx, best_ry)
        opp_dist_now = dist(nx, ny, ox, oy)
        # Also prefer separating from opponent while still moving.
        val = target_bonus + (opd - myd) * 1.5 + opp_dist_now * 0.08
        # Small preference to reduce steps if tied.
        val -= dist(nx, ny, best_rx, best_ry) * 0.01
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]