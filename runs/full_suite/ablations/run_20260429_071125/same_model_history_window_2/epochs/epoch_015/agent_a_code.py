def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if p is not None and len(p) == 2:
            obstacles.add((p[0], p[1]))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def edge_pen(x, y):
        return (1 if x == 0 else 0) + (1 if x == w - 1 else 0) + (1 if y == 0 else 0) + (1 if y == h - 1 else 0)

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx * dx + dy * dy

    # Choose best resource: prioritize ones I'm closer to; otherwise nearest among remaining.
    if resources:
        best = None
        for r in resources:
            rx, ry = r
            myd = dist2(sx, sy, rx, ry)
            opd = dist2(ox, oy, rx, ry)
            adv = myd - opd  # negative => I'm closer
            # Score tuple: prefer adv<0, then smaller myd, then deterministic by coords
            key = (0 if adv < 0 else 1, myd, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        # No resources: head toward opponent to contest space.
        tx, ty = ox, oy

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        d_to_target = cheb(nx, ny, tx, ty)

        # Extra shaping: reduce opponent's advantage toward the chosen target
        myd_next = dist2(nx, ny, tx, ty)
        opd_cur = dist2(ox, oy, tx, ty)
        adv_next = myd_next - opd_cur  # smaller is better for me

        # If stepping onto a resource, strongly prefer it (deterministic already)
        on_resource = 1 if (nx, ny) in set(map(tuple, resources)) else 0

        score = (-d_to_target * 1000) - (abs(adv_next) * 0.1) + on_resource * 10000 - edge_pen(nx, ny) * 0.25

        if score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            if (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]